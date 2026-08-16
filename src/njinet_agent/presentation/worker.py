from collections.abc import Sequence
from typing import Any, Optional

from arq.cron import CronJob
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function

from njinet_agent.agents.room_admin.agent import LangGraphAdminChatAgent
from njinet_agent.application.admin_chat import AdminChatRequest, handle_admin_chat
from njinet_agent.core.config import Settings, get_settings
from njinet_agent.infrastructure.callbacks.nestjs import NestJsAdminChatReplySender

Context = dict[str, Any]


async def run_admin_chat_job(
    ctx: Context,
    room_id: str,
    agent_id: str,
    agent_username: str,
    text: str,
    jwt: str,
    request_id: str,
) -> None:
    settings: Settings = ctx.get("settings") or get_settings()
    await handle_admin_chat(
        AdminChatRequest(room_id, agent_id, agent_username, text, jwt, request_id),
        agent=LangGraphAdminChatAgent(settings),
        reply_sender=NestJsAdminChatReplySender(settings),
    )


class WorkerSettings:
    functions: Sequence[WorkerCoroutine | Function] = [run_admin_chat_job]
    cron_jobs: Optional[Sequence[CronJob]] = None
    on_startup: Optional[StartupShutdown] = None
    on_shutdown: Optional[StartupShutdown] = None
