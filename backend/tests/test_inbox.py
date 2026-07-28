"""Knowledge Inbox: capture, promote to entry, and knowledge list filtering."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.admin import AdminAction
from app.models.enums import IdentityProvider, UserRole
from app.models.knowledge import KnowledgeEntry, KnowledgeInboxItem
from app.models.membership import Membership
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


async def test_inbox_capture_and_promote(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    inbox_id: uuid.UUID | None = None
    entry_id: uuid.UUID | None = None
    try:
        # Quick-capture a raw note.
        created = await client.post(
            "/api/admin/inbox",
            headers=auth,
            json={"content": "TEST remember to explain box breathing rhythm"},
        )
        assert created.status_code == 201
        assert created.json()["status"] == "new"
        inbox_id = uuid.UUID(created.json()["id"])

        # Promote it into a categorized draft entry.
        promoted = await client.post(
            f"/api/admin/inbox/{inbox_id}/promote",
            headers=auth,
            json={"title": "TEST Box breathing", "category": "breathing", "tags": ["breathing"]},
        )
        assert promoted.status_code == 200
        entry = promoted.json()
        assert entry["status"] == "draft"
        assert entry["category"] == "breathing"
        assert entry["body"] == "TEST remember to explain box breathing rhythm"
        entry_id = uuid.UUID(entry["id"])

        # The note is now marked promoted and linked to the entry.
        listed = await client.get("/api/admin/inbox?status_filter=promoted", headers=auth)
        row = next(r for r in listed.json() if r["id"] == str(inbox_id))
        assert row["promoted_entry_id"] == str(entry_id)

        # Re-promoting is rejected.
        again = await client.post(f"/api/admin/inbox/{inbox_id}/promote", headers=auth, json={})
        assert again.status_code == 409
    finally:
        if entry_id is not None:
            await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == inbox_id))
            await db_session.execute(delete(KnowledgeEntry).where(KnowledgeEntry.id == entry_id))
        if inbox_id is not None:
            await db_session.execute(
                delete(KnowledgeInboxItem).where(KnowledgeInboxItem.id == inbox_id)
            )
        await db_session.commit()


async def test_knowledge_filters(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    ids: list[uuid.UUID] = []
    try:
        marker = uuid.uuid4().hex[:8]
        a = await client.post(
            "/api/admin/knowledge",
            headers=auth,
            json={"title": f"TEST alpha {marker}", "body": "b", "category": f"cat-{marker}"},
        )
        b = await client.post(
            "/api/admin/knowledge",
            headers=auth,
            json={"title": f"TEST beta {marker}", "body": "b", "category": "other"},
        )
        ids = [uuid.UUID(a.json()["id"]), uuid.UUID(b.json()["id"])]

        # Category filter returns only the matching one.
        by_cat = await client.get(f"/api/admin/knowledge?category=cat-{marker}", headers=auth)
        cat_ids = {e["id"] for e in by_cat.json()}
        assert str(ids[0]) in cat_ids and str(ids[1]) not in cat_ids

        # Text search on the title.
        by_q = await client.get(f"/api/admin/knowledge?q=alpha {marker}", headers=auth)
        q_ids = {e["id"] for e in by_q.json()}
        assert str(ids[0]) in q_ids and str(ids[1]) not in q_ids
    finally:
        for i in ids:
            await db_session.execute(delete(KnowledgeEntry).where(KnowledgeEntry.id == i))
        await db_session.commit()
