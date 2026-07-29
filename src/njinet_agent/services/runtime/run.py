import logging

from langchain_core.runnables import RunnableConfig

from njinet_agent.core.config import Settings
from njinet_agent.services.agent.graph import build_graph
from njinet_agent.services.agent.llm import build_llm
from njinet_agent.services.events.publisher import send_reply
from njinet_agent.services.mcp.client import load_tools

logger = logging.getLogger(__name__)


async def run_agent(
    settings: Settings,
    room_id: str,
    agent_id: str,
    agent_username: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    try:
        tools = await load_tools(settings, jwt)
        llm = build_llm(settings)

        graph = build_graph(llm, tools)
        cfg: RunnableConfig = {"recursion_limit": settings.recursion_limit}
        result = await graph.ainvoke({"messages": [("user", text)]}, cfg)
        final_text = result["messages"][-1].content

        await send_reply(
            settings,
            room_id=room_id,
            agent_id=agent_id,
            agent_username=agent_username,
            request_id=request_id,
            status="final",
            text=final_text,
        )

    except Exception:
        logger.exception("run_agent failed for room %s request %s", room_id, request_id)

        await send_reply(
            settings,
            room_id=room_id,
            agent_id=agent_id,
            agent_username=agent_username,
            request_id=request_id,
            status="error",
            text="Something went wrong while processing your request.",
        )
