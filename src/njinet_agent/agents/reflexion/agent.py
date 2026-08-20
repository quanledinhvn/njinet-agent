from dataclasses import dataclass, field
from functools import cached_property

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from njinet_agent.agents.types import LLMFactory, SearchToolFactory
from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm
from njinet_agent.infrastructure.tools.search_tools import build_tavily_search_tool

from .prompts import draft_prompt, revise_prompt
from .schemas import AnswerQuestion, ReflexionState, ReviseAnswer


@dataclass
class ReflexionAgent:
    settings: Settings
    llm_factory: LLMFactory = build_openai_llm
    search_tool_factory: SearchToolFactory = build_tavily_search_tool
    max_iterations: int = 2

    # Built lazily, once, and reused across invoke() calls.
    _llm: BaseChatModel = field(init=False, repr=False)
    _search_tool: BaseTool = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._llm = self.llm_factory(self.settings)
        self._search_tool = self.search_tool_factory(self.settings)

    @cached_property
    def graph(self) -> CompiledStateGraph:
        builder = StateGraph(ReflexionState)

        builder.add_node("draft", self._draft_node)
        builder.add_node("tools", self._tool_node)
        builder.add_node("revise", self._revise_node)

        builder.add_edge(START, "draft")
        builder.add_edge("draft", "tools")
        builder.add_edge("tools", "revise")
        builder.add_conditional_edges("revise", self._should_continue, ["tools", END])

        return builder.compile()

    # --- Chains (built once, LLM reused) ---------------------------------
    @cached_property
    def _draft_chain(self) -> Runnable:
        return draft_prompt | self._llm.bind_tools(
            [AnswerQuestion], tool_choice=AnswerQuestion.__name__
        )

    @cached_property
    def _revise_chain(self) -> Runnable:
        return revise_prompt | self._llm.bind_tools(
            [ReviseAnswer], tool_choice=ReviseAnswer.__name__
        )

    @cached_property
    def _tool_node(self) -> ToolNode:
        def run_queries(search_queries: list[str], **_: object) -> list[object]:
            return self._search_tool.batch(
                [{"query": query} for query in search_queries]
            )

        return ToolNode(
            [
                StructuredTool.from_function(
                    run_queries,
                    name=AnswerQuestion.__name__,
                    args_schema=AnswerQuestion,
                ),
                StructuredTool.from_function(
                    run_queries,
                    name=ReviseAnswer.__name__,
                    args_schema=ReviseAnswer,
                ),
            ],
            # Surface tool failures as a ToolMessage instead of crashing the run,
            # so a flaky search API doesn't take down the whole graph.
            handle_tool_errors=True,
        )

    async def _draft_node(self, state: ReflexionState) -> dict[str, object]:
        response = await self._draft_chain.ainvoke({"messages": state["messages"]})
        return {"messages": [response], "revision_number": 0}

    async def _revise_node(self, state: ReflexionState) -> dict[str, object]:
        response = await self._revise_chain.ainvoke({"messages": state["messages"]})
        return {
            "messages": [response],
            "revision_number": state.get("revision_number", 0) + 1,
        }

    def _should_continue(self, state: ReflexionState) -> str:
        if state.get("revision_number", 0) >= self.max_iterations:
            return END
        return "tools"

    async def invoke(self, messages: list[BaseMessage]) -> dict[str, object]:
        initial_state: ReflexionState = {"messages": messages, "revision_number": 0}

        return await self.graph.ainvoke(initial_state)
