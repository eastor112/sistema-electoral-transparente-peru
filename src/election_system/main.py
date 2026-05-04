from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from election_system.api.v1.router import api_router
from election_system.core.config import settings
from election_system.core.logging import configure_logging

_logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    # TODO: initialize DB connections, caches, and background workers.
    yield
    # TODO: graceful shutdown for external resources.


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that prevents stack-trace leakage on unexpected errors."""
    _logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        exc_type=type(exc).__name__,
        exc=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
