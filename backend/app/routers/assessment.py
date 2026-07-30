"""Customer-facing assessment routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.assessment import BackgroundAssessment
from app.models.user import User
from app.schemas.assessment import AssessmentAnswers, AssessmentRead
from app.services import assessment as svc

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.get("", response_model=AssessmentRead | None)
async def get_assessment(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BackgroundAssessment | None:
    return await svc.get_user_assessment(db, user.id)


@router.post("/submit", response_model=AssessmentRead)
async def submit_assessment(
    payload: AssessmentAnswers,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BackgroundAssessment:
    item = await svc.upsert_assessment(db, user.id, payload.model_dump())
    await db.commit()
    return item
