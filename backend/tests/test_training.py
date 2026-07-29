"""Training Stage + Module manager: CRUD, next-refs, duplicate key, gating."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.training import TrainingModule, TrainingStage
from app.models.user import User, UserIdentity
from tests.conftest import TEST_EMAIL_DOMAIN


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


async def test_stage_and_module_crud_with_next_refs(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    auth = await _admin_headers(db_session)
    m = uuid.uuid4().hex[:8]
    stage_ids: list[uuid.UUID] = []
    module_ids: list[uuid.UUID] = []
    try:
        # Create two stages.
        s1 = await client.post(
            "/api/admin/stages",
            headers=auth,
            json={"key": f"beginner-{m}", "name": "Beginner", "order_index": 1},
        )
        s2 = await client.post(
            "/api/admin/stages",
            headers=auth,
            json={"key": f"basic-{m}", "name": "Basic Training", "order_index": 2},
        )
        assert s1.status_code == 201 and s2.status_code == 201
        stage_ids = [uuid.UUID(s1.json()["id"]), uuid.UUID(s2.json()["id"])]

        # Duplicate stage key -> 409.
        dup = await client.post(
            "/api/admin/stages",
            headers=auth,
            json={"key": f"beginner-{m}", "name": "Dup"},
        )
        assert dup.status_code == 409

        # Create two modules; module1 points "next" at module2 and stage2, gated to $199.
        mod2 = await client.post(
            "/api/admin/training-modules",
            headers=auth,
            json={"key": f"scan-{m}", "name": "Body scan", "stage_id": str(stage_ids[1])},
        )
        assert mod2.status_code == 201
        module_ids.append(uuid.UUID(mod2.json()["id"]))

        mod1 = await client.post(
            "/api/admin/training-modules",
            headers=auth,
            json={
                "key": f"breath-{m}",
                "name": "5-min breathing",
                "stage_id": str(stage_ids[0]),
                "steps": ["Sit comfortably", "Inhale 4", "Exhale 4"],
                "duration_minutes": 5,
                "next_module_id": mod2.json()["id"],
                "next_stage_id": str(stage_ids[1]),
                "min_ai_level": "energy_guide",
            },
        )
        assert mod1.status_code == 201
        body = mod1.json()
        module_ids.append(uuid.UUID(body["id"]))

        # next refs + gating + steps persisted.
        assert body["next_module_id"] == mod2.json()["id"]
        assert body["next_stage_id"] == str(stage_ids[1])
        assert body["min_ai_level"] == "energy_guide"
        assert body["steps"] == ["Sit comfortably", "Inhale 4", "Exhale 4"]
        assert body["duration_minutes"] == 5

        # Update a module.
        patched = await client.patch(
            f"/api/admin/training-modules/{body['id']}",
            headers=auth,
            json={"duration_minutes": 8},
        )
        assert patched.status_code == 200
        assert patched.json()["duration_minutes"] == 8

        # Lists include our items.
        stages = await client.get("/api/admin/stages", headers=auth)
        assert {str(i) for i in stage_ids} <= {s["id"] for s in stages.json()}
    finally:
        for i in module_ids:
            await db_session.execute(delete(TrainingModule).where(TrainingModule.id == i))
        for i in stage_ids:
            await db_session.execute(delete(TrainingStage).where(TrainingStage.id == i))
        await db_session.commit()


async def test_training_requires_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/admin/stages")).status_code == 401
    assert (await client.get("/api/admin/training-modules")).status_code == 401
