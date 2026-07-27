"""Knowledge Manager: CRUD + audited draft→publish→unpublish workflow."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.admin import AdminAction
from app.models.enums import IdentityProvider, UserRole
from app.models.knowledge import KnowledgeEntry
from app.models.membership import Membership
from app.models.user import User, UserIdentity
from tests.conftest import TEST_EMAIL_DOMAIN


async def _make_admin(db: AsyncSession) -> tuple[uuid.UUID, str]:
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
    token = create_access_token(subject=str(admin.id), role=UserRole.admin.value)
    return admin.id, token


async def test_knowledge_crud_and_status_workflow(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _, token = await _make_admin(db_session)
    auth = {"Authorization": f"Bearer {token}"}
    entry_id: uuid.UUID | None = None
    try:
        # Create a draft.
        created = await client.post(
            "/api/admin/knowledge",
            headers=auth,
            json={
                "title": "TEST Box breathing",
                "body": "Inhale 4, hold 4, exhale 4.",
                "category": "breathing",
                "tags": ["breathing"],
                "min_ai_level": "basic_chat",
            },
        )
        assert created.status_code == 201
        body = created.json()
        assert body["status"] == "draft"
        entry_id = uuid.UUID(body["id"])

        # Appears in list + detail.
        listed = await client.get("/api/admin/knowledge", headers=auth)
        assert listed.status_code == 200
        assert any(e["id"] == str(entry_id) for e in listed.json())

        # Update ignores status (only content fields are editable here).
        patched = await client.patch(
            f"/api/admin/knowledge/{entry_id}",
            headers=auth,
            json={"title": "TEST Box breathing v2", "status": "published"},
        )
        assert patched.status_code == 200
        assert patched.json()["title"] == "TEST Box breathing v2"
        assert patched.json()["status"] == "draft"  # status change ignored

        # Publish, then unpublish.
        pub = await client.post(f"/api/admin/knowledge/{entry_id}/publish", headers=auth)
        assert pub.status_code == 200
        assert pub.json()["status"] == "published"

        unpub = await client.post(f"/api/admin/knowledge/{entry_id}/unpublish", headers=auth)
        assert unpub.status_code == 200
        assert unpub.json()["status"] == "unpublished"

        # Detail reflects the final state.
        detail = await client.get(f"/api/admin/knowledge/{entry_id}", headers=auth)
        assert detail.json()["status"] == "unpublished"

        # Both transitions are in the audit trail.
        actions = (
            (await db_session.execute(select(AdminAction).where(AdminAction.entity_id == entry_id)))
            .scalars()
            .all()
        )
        recorded = {a.action for a in actions}
        assert "knowledge.publish" in recorded
        assert "knowledge.unpublish" in recorded
    finally:
        if entry_id is not None:
            await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == entry_id))
            await db_session.execute(delete(KnowledgeEntry).where(KnowledgeEntry.id == entry_id))
            await db_session.commit()


async def test_knowledge_requires_admin(client: AsyncClient) -> None:
    # No token -> 401.
    assert (await client.get("/api/admin/knowledge")).status_code == 401
    # Customer token -> 403.
    signup = await client.post(
        "/api/auth/signup",
        json={"email": f"cust_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}", "password": "customer12"},
    )
    token = signup.json()["access_token"]
    resp = await client.get("/api/admin/knowledge", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
