"""Sales trigger + Risk & Safety (risk rules + blocked claims) managers."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.rules import BlockedClaim, RiskRule, SalesTrigger
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


async def test_sales_trigger_allow_and_block(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    ids: list[uuid.UUID] = []
    try:
        block = await client.post(
            "/api/admin/sales-triggers",
            headers=auth,
            json={
                "name": f"TEST block {uuid.uuid4().hex[:6]}",
                "conditions": {"intents": ["discomfort"]},
                "mode": "block",
                "priority": 1,
                "status": "active",
            },
        )
        assert block.status_code == 201
        assert block.json()["mode"] == "block"
        assert block.json()["conditions"]["intents"] == ["discomfort"]
        ids.append(uuid.UUID(block.json()["id"]))

        allow = await client.post(
            "/api/admin/sales-triggers",
            headers=auth,
            json={
                "name": f"TEST allow {uuid.uuid4().hex[:6]}",
                "conditions": {"intents": ["price_question"]},
                "mode": "allow",
                "target_package": "coaching_199",
                "priority": 60,
            },
        )
        assert allow.status_code == 201
        assert allow.json()["mode"] == "allow"
        assert allow.json()["target_package"] == "coaching_199"
        ids.append(uuid.UUID(allow.json()["id"]))

        # Ordered by priority (block first).
        listed = await client.get("/api/admin/sales-triggers", headers=auth)
        ours = [t for t in listed.json() if t["id"] in {str(i) for i in ids}]
        assert ours[0]["mode"] == "block"
    finally:
        for i in ids:
            await db_session.execute(delete(SalesTrigger).where(SalesTrigger.id == i))
        await db_session.commit()


async def test_risk_rule_and_blocked_claim(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    rule_id: uuid.UUID | None = None
    claim_id: uuid.UUID | None = None
    term = f"testterm_{uuid.uuid4().hex[:8]}"
    try:
        # Risk rule with keywords + severity + fallback.
        rr = await client.post(
            "/api/admin/risk-rules",
            headers=auth,
            json={
                "category": f"test_{uuid.uuid4().hex[:6]}",
                "keywords": ["chest pain", "dizziness"],
                "severity": "high",
                "fallback_action": {"type": "safety_first", "disable_sales": True},
            },
        )
        assert rr.status_code == 201
        assert rr.json()["keywords"] == ["chest pain", "dizziness"]
        assert rr.json()["severity"] == "high"
        rule_id = uuid.UUID(rr.json()["id"])

        # It's queryable in the list.
        rules = await client.get("/api/admin/risk-rules", headers=auth)
        assert any(r["id"] == str(rule_id) for r in rules.json())

        # Blocked-claim word list: add, duplicate rejected.
        bc = await client.post("/api/admin/blocked-claims", headers=auth, json={"term": term})
        assert bc.status_code == 201
        claim_id = uuid.UUID(bc.json()["id"])
        dup = await client.post("/api/admin/blocked-claims", headers=auth, json={"term": term})
        assert dup.status_code == 409
    finally:
        if claim_id is not None:
            await db_session.execute(delete(BlockedClaim).where(BlockedClaim.id == claim_id))
        if rule_id is not None:
            await db_session.execute(delete(RiskRule).where(RiskRule.id == rule_id))
        await db_session.commit()


async def test_sales_risk_require_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/admin/sales-triggers")).status_code == 401
    assert (await client.get("/api/admin/risk-rules")).status_code == 401
    assert (await client.get("/api/admin/blocked-claims")).status_code == 401
