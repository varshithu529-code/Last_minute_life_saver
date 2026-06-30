"""Health check endpoint."""

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.schemas import HealthResponse
from app.services.cache import cache_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Service health including DB and Redis status."""
    settings = get_settings()
    db_status = "ok"
    try:
        from sqlalchemy import text

        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        version=__version__,
        database=db_status,
        redis="ok" if cache_service.available else "disabled",
    )
