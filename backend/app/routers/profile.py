"""Customer-facing Energy Profile route."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.assessment import EnergyProfile
from app.models.user import User
from app.schemas.profile import ProfileRead

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileRead | None)
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EnergyProfile | None:
    return (
        await db.execute(select(EnergyProfile).where(EnergyProfile.user_id == user.id))
    ).scalar_one_or_none()
