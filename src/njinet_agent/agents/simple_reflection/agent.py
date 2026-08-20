from dataclasses import dataclass, field
from functools import cached_property

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from njinet_agent.agents.types import LLMFactory
from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm

from .prompts import generation_prompt, reflection_prompt
from .schemas import MessageGraph


@dataclass
class SimpleReflectionAgent:
    settings: Settings
    llm_factory: LLMFactory = build_openai_llm
    _llm: BaseChatModel = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._llm = self.llm_factory(self.settings)

    @cached_property
    def _generation_chain(self) -> Runnable:
        return generation_prompt | self._llm

    @cached_property
    def _reflection_chain(self) -> Runnable:
        return reflection_prompt | self._llm

    @cached_property
    def graph(self) -> CompiledStateGraph:
        REFLECT = "reflect"
        GENERATE = "generate"

        async def generation_node(state: MessageGraph):
            return {
                "messages": [
                    await self._generation_chain.ainvoke(
                        {"messages": state["messages"]}
                    )
                ]
            }

        async def reflection_node(state: MessageGraph):
            res = await self._reflection_chain.ainvoke(
                {"messages": state["messages"]}
            )
            return {"messages": [HumanMessage(content=res.content)]}

        def should_continue(state: MessageGraph):
            if len(state["messages"]) > 6:
                return END
            return REFLECT

        builder = StateGraph(state_schema=MessageGraph)
        builder.add_node(GENERATE, generation_node)
        builder.add_node(REFLECT, reflection_node)
        builder.set_entry_point(GENERATE)

        builder.add_conditional_edges(GENERATE, should_continue)
        builder.add_edge(REFLECT, GENERATE)

        return builder.compile()

    async def invoke(self, message: MessageGraph):
        return await self.graph.ainvoke(message)
