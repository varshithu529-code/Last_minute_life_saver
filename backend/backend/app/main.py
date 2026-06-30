"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app import __version__
from app.api.v1 import api_router
from app.config import get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB. Shutdown: cleanup."""
    settings = get_settings()
    setup_logging(settings.debug)
    init_db()
    yield


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Autonomous Productivity Companion — API-first hackathon POC",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def root():
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        }

    return app


app = create_app()
