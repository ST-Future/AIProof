"""Health check endpoint.

Verifies the service is up and, best-effort, that the database is reachable.
Used by the frontend and by hosting platform health probes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    settings = get_settings()
    database = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - health must never raise
        database = "unavailable"

    return HealthResponse(
        status="ok",
        service="great-energy-field-backend",
        env=settings.app_env,
        database=database,
    )
