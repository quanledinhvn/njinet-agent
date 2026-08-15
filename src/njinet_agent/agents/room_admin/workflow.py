from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from njinet_agent.agents.room_admin.prompt import ORCHESTRATOR_SYSTEM_PROMPT


class RoomAdminWorkflow:
    def build_graph(
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

    async def invoke(
        self,
        llm: BaseChatModel,
        tools: list[BaseTool],
        text: str,
        recursion_limit: int,
    ) -> str:
        result = await self.build_graph(llm, tools).ainvoke(
            {"messages": [("user", text)]}, {"recursion_limit": recursion_limit}
        )
        return result["messages"][-1].content
