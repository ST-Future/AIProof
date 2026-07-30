"""Background assessment: submit persists, re-submit updates (no duplicate)."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import BackgroundAssessment
from app.models.user import User
from tests.conftest import TEST_EMAIL_DOMAIN

ANSWERS = {
    "experience": "beginner",
    "stress_level": "high",
    "sleep_quality": "fair",
    "energy_level": "low",
    "goals": ["more_energy", "better_sleep"],
    "minutes_per_day": 10,
    "notes": "prefers mornings",
}


async def _signup(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/auth/signup",
        json={"email": f"user_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}", "password": "password12"},
    )
    return resp.json()["access_token"]


async def test_submit_then_resubmit_updates(client: AsyncClient, db_session: AsyncSession) -> None:
    token = await _signup(client)
    auth = {"Authorization": f"Bearer {token}"}

    # Initially no assessment.
    assert (await client.get("/api/assessment", headers=auth)).json() is None

    # First submit persists version 1.
    first = await client.post("/api/assessment/submit", headers=auth, json=ANSWERS)
    assert first.status_code == 200
    body = first.json()
    assert body["version"] == 1
    assert body["answers"]["experience"] == "beginner"
    assessment_id = body["id"]

    # Re-submit updates the same row (version bumps, id unchanged, no duplicate).
    changed = {**ANSWERS, "stress_level": "low", "notes": "feeling better"}
    second = await client.post("/api/assessment/submit", headers=auth, json=changed)
    assert second.status_code == 200
    assert second.json()["id"] == assessment_id
    assert second.json()["version"] == 2
    assert second.json()["answers"]["stress_level"] == "low"

    # Exactly one row exists for this user.
    user_id = uuid.UUID((await client.get("/api/auth/me", headers=auth)).json()["id"])
    count = (
        await db_session.execute(
            select(func.count())
            .select_from(BackgroundAssessment)
            .where(BackgroundAssessment.user_id == user_id)
        )
    ).scalar_one()
    assert count == 1

    # cleanup (deleting the user cascades to the assessment)
    await db_session.execute(delete(User).where(User.id == user_id))
    await db_session.commit()


async def test_invalid_answers_rejected(client: AsyncClient) -> None:
    token = await _signup(client)
    auth = {"Authorization": f"Bearer {token}"}
    bad = {**ANSWERS, "stress_level": "extreme"}  # not an allowed value
    resp = await client.post("/api/assessment/submit", headers=auth, json=bad)
    assert resp.status_code == 422


async def test_assessment_requires_auth(client: AsyncClient) -> None:
    assert (await client.get("/api/assessment")).status_code == 401
    assert (await client.post("/api/assessment/submit", json=ANSWERS)).status_code == 401
