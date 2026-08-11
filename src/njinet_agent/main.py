import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import create_worker
from dotenv import load_dotenv
from fastapi import FastAPI

from njinet_agent.api.v1.endpoints import health
from njinet_agent.api.v1.router import api_router
from njinet_agent.core.config import Settings, get_settings
from njinet_agent.core.exceptions import register_exception_handlers
from njinet_agent.core.middleware import register_middleware
from njinet_agent.services.runtime.worker import WorkerSettings

logging.basicConfig(level=logging.INFO)
load_dotenv()  # LangSmith reads os.environ, not pydantic Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))

    worker = create_worker(WorkerSettings, handle_signals=False)
    task = asyncio.create_task(worker.async_run())

    try:
        yield
    finally:
        # arq.close() cancels main_task on purpose; shield so Ctrl+C can't abort cleanup
        async def shutdown():
            await worker.close()
            with suppress(asyncio.CancelledError):
                await task
            await app.state.arq_pool.aclose()

        with suppress(asyncio.CancelledError):
            await asyncio.shield(shutdown())


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title="njinet-agent", lifespan=lifespan)

    register_middleware(app, settings)
    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
