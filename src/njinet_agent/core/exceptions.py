from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AgentError(Exception):
    """Business error raised by the agent service."""

    status_code = 500
    code = "agent_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EnqueueError(AgentError):
    """Failed to push a job onto the arq queue."""

    status_code = 503
    code = "enqueue_failed"


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AgentError)
    async def handle_agent_error(request: Request, exc: AgentError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body("http_error", str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "invalid request body")
            | {"detail": exc.errors()},
        )
