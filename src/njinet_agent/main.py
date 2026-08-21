import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import create_worker
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.language_models import BaseChatModel

from njinet_agent.agents.room_admin.agent import LangGraphAdminChatAgent
from njinet_agent.core.config import Settings, get_settings
from njinet_agent.infrastructure.llm.openai import build_openai_llm
from njinet_agent.infrastructure.queue.arq import ArqAdminChatQueue
from njinet_agent.presentation.http.api.agent import router as agent_router
from njinet_agent.presentation.http.api.health import router as health_router
from njinet_agent.presentation.http.exception_handlers import (
    register_exception_handlers,
)
from njinet_agent.presentation.http.request_middleware import register_middleware
from njinet_agent.presentation.worker import WorkerSettings

logging.basicConfig(level=logging.INFO)
load_dotenv()  # LangSmith reads os.environ, not pydantic Settings


def create_app(
    settings: Settings | None = None, llm: BaseChatModel | None = None
) -> FastAPI:
    if settings is None:
        settings = get_settings()
    if llm is None:
        llm = build_openai_llm(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        redis_settings = RedisSettings.from_dsn(settings.redis_url)
        app.state.arq_pool = await create_pool(redis_settings)
        app.state.admin_chat_queue = ArqAdminChatQueue(app.state.arq_pool)

        class AppWorkerSettings(WorkerSettings):
            pass

        async def worker_startup(ctx):
            ctx["settings"] = settings
            ctx["admin_chat_agent"] = LangGraphAdminChatAgent(settings, llm)

        AppWorkerSettings.redis_settings = redis_settings
        AppWorkerSettings.on_startup = worker_startup
        worker = create_worker(AppWorkerSettings, handle_signals=False)
        task = asyncio.create_task(worker.async_run())

        try:
            yield
        finally:
            # arq.close() cancels main_task on purpose; shield cleanup from Ctrl+C
            async def shutdown():
                await worker.close()
                with suppress(asyncio.CancelledError):
                    await task
                await app.state.arq_pool.aclose()

            with suppress(asyncio.CancelledError):
                await asyncio.shield(shutdown())

    app = FastAPI(title="njinet-agent", lifespan=lifespan)
    app.state.llm = llm

    register_middleware(app, settings)
    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(agent_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
