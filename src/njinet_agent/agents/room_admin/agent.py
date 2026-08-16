from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from njinet_agent.agents.room_admin.prompt import ORCHESTRATOR_SYSTEM_PROMPT
from njinet_agent.application.admin_chat import AdminChatReply, AdminChatRequest
from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm
from njinet_agent.infrastructure.mcp.client import load_tools

ToolLoader = Callable[[Settings, str], Awaitable[list[BaseTool]]]
LLMFactory = Callable[[Settings], BaseChatModel]


@dataclass
class LangGraphAdminChatAgent:
    settings: Settings
    llm_factory: LLMFactory = build_openai_llm
    tool_loader: ToolLoader = load_tools

    def _build_graph(
        self, llm: BaseChatModel, tools: list[BaseTool]
    ) -> CompiledStateGraph:
        llm_with_tools = llm.bind_tools(tools)

        async def agent(state: MessagesState):
            messages = [SystemMessage(ORCHESTRATOR_SYSTEM_PROMPT), *state["messages"]]
            return {"messages": [await llm_with_tools.ainvoke(messages)]}

        graph = StateGraph(MessagesState)
        graph.add_node("agent", agent)
        graph.add_node("tools", ToolNode(tools))
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", "agent")
        return graph.compile()

    async def reply(self, request: AdminChatRequest) -> AdminChatReply:
        tools = await self.tool_loader(self.settings, request.jwt)
        result = await self._build_graph(
            self.llm_factory(self.settings), tools
        ).ainvoke(
            {"messages": [("user", request.text)]},
            {"recursion_limit": self.settings.recursion_limit},
        )
        return AdminChatReply(text=result["messages"][-1].content)
