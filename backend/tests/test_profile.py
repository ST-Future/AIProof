"""Energy Profile + initial training state + admin customers directory."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.assessment import EnergyProfile
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.training import UserTrainingState
from app.models.user import User, UserIdentity
from tests.conftest import TEST_EMAIL_DOMAIN

ANSWERS = {
    "experience": "beginner",
    "stress_level": "high",
    "sleep_quality": "fair",
    "energy_level": "low",
    "goals": ["more_energy", "better_sleep"],
    "minutes_per_day": 10,
    "notes": None,
}


async def _admin_headers(db: AsyncSession) -> dict[str, str]:
    admin = User(display_name="Founder", role=UserRole.admin)
    admin.identities.append(
        UserIdentity(
            provider=IdentityProvider.email,
            identifier=f"admin_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}",
            password_hash="x",
            is_primary=True,
        )
    )
    admin.membership = Membership()
    db.add(admin)
    await db.commit()
    return {"Authorization": f"Bearer {create_access_token(str(admin.id), UserRole.admin.value)}"}


async def test_assessment_generates_profile_and_state_idempotently(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    signup = await client.post(
        "/api/auth/signup",
        json={"email": f"user_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}", "password": "password12"},
    )
    auth = {"Authorization": f"Bearer {signup.json()['access_token']}"}
    user_id = uuid.UUID(signup.json()["user"]["id"])

    # Submit assessment -> profile + training state created.
    await client.post("/api/assessment/submit", headers=auth, json=ANSWERS)

    prof = await client.get("/api/profile", headers=auth)
    assert prof.status_code == 200
    body = prof.json()
    assert body is not None
    assert body["summary"]
    assert body["traits"]["intensity"] == "gentle"  # high stress / low energy
    assert body["traits"]["level"] == "beginner"

    async def counts() -> tuple[int, int]:
        p = (
            await db_session.execute(
                select(func.count())
                .select_from(EnergyProfile)
                .where(EnergyProfile.user_id == user_id)
            )
        ).scalar_one()
        s = (
            await db_session.execute(
                select(func.count())
                .select_from(UserTrainingState)
                .where(UserTrainingState.user_id == user_id)
            )
        ).scalar_one()
        return p, s

    assert await counts() == (1, 1)

    # Training state started at the "beginner" stage, day 0.
    state = (
        await db_session.execute(
            select(UserTrainingState).where(UserTrainingState.user_id == user_id)
        )
    ).scalar_one()
    assert state.current_stage_id is not None
    assert state.day_count == 0
    assert state.completed_sessions == 0

    # Simulate progress, then re-submit — profile updates, progress is NOT reset.
    state.completed_sessions = 4
    await db_session.commit()

    await client.post("/api/assessment/submit", headers=auth, json={**ANSWERS, "notes": "hi"})
    assert await counts() == (1, 1)  # still one each

    state2 = (
        await db_session.execute(
            select(UserTrainingState).where(UserTrainingState.user_id == user_id)
        )
    ).scalar_one()
    assert state2.completed_sessions == 4  # preserved

    await db_session.execute(delete(User).where(User.id == user_id))
    await db_session.commit()


async def test_admin_customers_lists_state(client: AsyncClient, db_session: AsyncSession) -> None:
    admin_auth = await _admin_headers(db_session)
    signup = await client.post(
        "/api/auth/signup",
        json={
            "email": f"user_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}",
            "password": "password12",
            "display_name": "Practicer",
        },
    )
    user_id = uuid.UUID(signup.json()["user"]["id"])
    user_auth = {"Authorization": f"Bearer {signup.json()['access_token']}"}
    try:
        await client.post("/api/assessment/submit", headers=user_auth, json=ANSWERS)

        rows = await client.get("/api/admin/customers", headers=admin_auth)
        assert rows.status_code == 200
        row = next(r for r in rows.json() if r["id"] == str(user_id))
        assert row["has_assessment"] is True
        assert row["energy_summary"]
        assert row["stage"] == "Beginner"
        assert row["day_count"] == 0
    finally:
        await db_session.execute(delete(User).where(User.id == user_id))
        await db_session.commit()


async def test_customers_requires_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/admin/customers")).status_code == 401
