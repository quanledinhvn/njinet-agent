from collections.abc import Sequence
from typing import Any, Optional

from arq.connections import RedisSettings
from arq.cron import CronJob
from arq.typing import WorkerCoroutine
from arq.worker import Function

from njinet_agent.core.config import get_settings
from njinet_agent.services.runtime.run import run_agent

Context = dict[str, Any]


async def run_agent_job(
    ctx: Context,
    room_id: str,
    agent_id: str,
    agent_username: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    settings = get_settings()

    await run_agent(
        settings, room_id, agent_id, agent_username, text, jwt, request_id
    )


class WorkerSettings:
    functions: Sequence[WorkerCoroutine | Function] = [run_agent_job]
    cron_jobs: Optional[Sequence[CronJob]] = None
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
