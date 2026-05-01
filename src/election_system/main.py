from contextlib import asynccontextmanager

from fastapi import FastAPI

from election_system.api.v1.router import api_router
from election_system.core.config import settings
from election_system.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    # TODO: initialize DB connections, caches, and background workers.
    yield
    # TODO: graceful shutdown for external resources.


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
