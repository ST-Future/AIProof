"""Agent rules manager: CRUD, priority ordering, safety flag, JSON persistence."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.rules import AgentRule
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


async def test_rule_crud_priority_and_safety(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    m = uuid.uuid4().hex[:8]
    ids: list[uuid.UUID] = []
    try:
        # A safety-override rule at top priority with structured conditions/actions.
        safety = await client.post(
            "/api/admin/rules",
            headers=auth,
            json={
                "name": f"TEST safety {m}",
                "conditions": {"intents": ["discomfort"], "risks": ["cardiac"]},
                "actions": {"type": "safety_first", "disable_sales": True},
                "priority": 1,
                "status": "active",
                "is_safety_override": True,
            },
        )
        assert safety.status_code == 201
        sbody = safety.json()
        ids.append(uuid.UUID(sbody["id"]))
        # Structured JSON persisted (not free text) + flag set.
        assert sbody["conditions"]["risks"] == ["cardiac"]
        assert sbody["actions"]["type"] == "safety_first"
        assert sbody["is_safety_override"] is True

        # A lower-priority sales rule.
        sales = await client.post(
            "/api/admin/rules",
            headers=auth,
            json={
                "name": f"TEST sales {m}",
                "conditions": {"intents": ["price_question"]},
                "actions": {"type": "allow_sales", "allow_sales": True},
                "priority": 60,
            },
        )
        assert sales.status_code == 201
        ids.append(uuid.UUID(sales.json()["id"]))
        assert sales.json()["status"] == "draft"  # default

        # Listed ordered by priority (safety first). Filter to our two rules.
        listed = await client.get("/api/admin/rules", headers=auth)
        ours = [r for r in listed.json() if r["id"] in {str(i) for i in ids}]
        assert [r["name"] for r in ours] == [f"TEST safety {m}", f"TEST sales {m}"]

        # Reorder by priority: push the sales rule above safety.
        patched = await client.patch(
            f"/api/admin/rules/{ids[1]}",
            headers=auth,
            json={"priority": 0, "status": "active"},
        )
        assert patched.status_code == 200
        assert patched.json()["priority"] == 0
        listed2 = await client.get("/api/admin/rules", headers=auth)
        ours2 = [r for r in listed2.json() if r["id"] in {str(i) for i in ids}]
        assert ours2[0]["name"] == f"TEST sales {m}"

        # Delete one.
        assert (await client.delete(f"/api/admin/rules/{ids[0]}", headers=auth)).status_code == 204
    finally:
        for i in ids:
            await db_session.execute(delete(AgentRule).where(AgentRule.id == i))
        await db_session.commit()


async def test_rules_require_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/admin/rules")).status_code == 401
