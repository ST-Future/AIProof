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
from app.services import profile as profile_svc

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

    # Generate the Energy Profile and ensure a training state exist (idempotent).
    summary, traits = profile_svc.generate_energy_profile(item.answers)
    await profile_svc.upsert_energy_profile(
        db, user.id, source_assessment_id=item.id, summary=summary, traits=traits
    )
    await profile_svc.initialize_training_state(
        db, user.id, stage_key=profile_svc.starting_stage_key(item.answers)
    )

    await db.commit()
    return item
