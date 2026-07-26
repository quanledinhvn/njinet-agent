from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from njinet_agent.core.config import Settings


@asynccontextmanager
async def open_checkpointer(settings: Settings):
  async with AsyncPostgresSaver.from_conn_string(settings.database_url) as cp:
    yield cp