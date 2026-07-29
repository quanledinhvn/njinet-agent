from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from njinet_agent.services.agent.prompts import ORCHESTRATOR_SYSTEM_PROMPT


def build_graph(
    llm: BaseChatModel,
    tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    llm_with_tools = llm.bind_tools(tools)

    async def agent(state: MessagesState):
        messages = [SystemMessage(ORCHESTRATOR_SYSTEM_PROMPT), *state["messages"]]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    g = StateGraph(MessagesState)

    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(tools))

    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")

    return g.compile(checkpointer=checkpointer)
