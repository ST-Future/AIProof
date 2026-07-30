"""Assessment service: one assessment per user, upserted on re-submit."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import BackgroundAssessment


async def get_user_assessment(db: AsyncSession, user_id: uuid.UUID) -> BackgroundAssessment | None:
    stmt = (
        select(BackgroundAssessment)
        .where(BackgroundAssessment.user_id == user_id)
        .order_by(BackgroundAssessment.created_at.desc())
    )
    return (await db.execute(stmt)).scalars().first()


async def upsert_assessment(
    db: AsyncSession, user_id: uuid.UUID, answers: dict[str, Any]
) -> BackgroundAssessment:
    """Create the user's assessment, or update it in place on re-submit."""
    now = datetime.now(UTC)
    item = await get_user_assessment(db, user_id)
    if item is not None:
        item.answers = answers
        item.version += 1
        item.submitted_at = now
    else:
        item = BackgroundAssessment(user_id=user_id, answers=answers, version=1, submitted_at=now)
        db.add(item)
    await db.flush()
    await db.refresh(item)
    return item
