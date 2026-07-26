from langchain_core.runnables import RunnableConfig
from redis.asyncio import Redis

from njinet_agent.core.config import Settings
from njinet_agent.services.agent.graph import build_graph
from njinet_agent.services.agent.llm import build_llm
from njinet_agent.services.events.publisher import publish
from njinet_agent.services.events.types import AgentEvent
from njinet_agent.services.mcp.client import load_tools
from njinet_agent.services.runtime.checkpointer import open_checkpointer


async def run_agent(
    settings: Settings,
    redis: Redis,
    room_id: str,
    actor_id: str,
    text: str,
    jwt: str,
) -> None:
    try:
        tools = await load_tools(settings, actor_id, room_id, jwt)
        llm = build_llm(settings)

        async with open_checkpointer(settings) as checkpointer:
            graph = build_graph(llm, tools, checkpointer)
            cfg: RunnableConfig = {
                "configurable": {"thread_id": f"room:{room_id}"},
                "recursion_limit": settings.recursion_limit,
            }
            result = await graph.ainvoke({"messages": [("user", text)]}, cfg)
            final_text = result["messages"][-1].content

            await publish(
                redis, room_id, AgentEvent(type="final", data={"text": final_text})
            )

    except Exception as exc:
        await publish(
            redis, room_id, AgentEvent(type="error", data={"message": str(exc)})
        )