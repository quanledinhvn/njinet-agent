import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from njinet_agent.core.config import Settings

logger = logging.getLogger("njinet_agent.request")


def register_middleware(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # pyright: ignore[reportUnusedFunction]
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        started = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            extra={"request_id": request_id},
        )
        response.headers["X-Request-Id"] = request_id
        return response
