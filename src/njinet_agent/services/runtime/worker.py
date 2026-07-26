from collections.abc import Sequence
from typing import Any, Optional

from arq.connections import RedisSettings
from arq.cron import CronJob
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function
from redis.asyncio import Redis

from njinet_agent.core.config import get_settings
from njinet_agent.services.runtime.run import run_agent

Context = dict[str, Any]


async def run_agent_job(
    ctx: Context,
    room_id: str,
    actor_id: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    settings = get_settings()
    redis: Redis = ctx["publish_redis"]
    await run_agent(settings, redis, room_id, actor_id, text, jwt)


async def on_startup(ctx: Context) -> None:
    settings = get_settings()
    ctx["publish_redis"] = Redis.from_url(settings.redis_url)


async def on_shutdown(ctx: Context) -> None:
    await ctx["publish_redis"].aclose()


class WorkerSettings:
    functions: Sequence[WorkerCoroutine | Function] = [run_agent_job]
    cron_jobs: Optional[Sequence[CronJob]] = None
    on_startup: Optional[StartupShutdown] = on_startup
    on_shutdown: Optional[StartupShutdown] = on_shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
