"""RAG pipeline: publish embeds, search returns relevant published chunks,
unpublish excludes, re-publish re-embeds, and package-level filtering."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.admin import AdminAction
from app.models.enums import AiLevel, IdentityProvider, UserRole
from app.models.knowledge import KnowledgeEntry
from app.models.membership import Membership
from app.models.user import User, UserIdentity
from app.services import embeddings as emb
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


async def _create(client: AsyncClient, auth: dict[str, str], **body: object) -> str:
    resp = await client.post("/api/admin/knowledge", headers=auth, json=body)
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_publish_embeds_and_search(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    marker = uuid.uuid4().hex[:8]
    breathing_id = await _create(
        client,
        auth,
        title=f"Box breathing {marker}",
        body="Box breathing rhythm: inhale four, hold four, exhale four, hold four.",
        category="breathing",
    )
    sleep_id = await _create(
        client,
        auth,
        title=f"Evening wind down {marker}",
        body="A calming evening routine to relax the body before sleep and rest deeply.",
        category="sleep",
    )
    ids = [uuid.UUID(breathing_id), uuid.UUID(sleep_id)]
    try:
        # Not yet published -> no results.
        assert await emb.search(db_session, f"box breathing {marker}") == []

        # Publish both -> embeddings generated.
        for i in ids:
            await client.post(f"/api/admin/knowledge/{i}/publish", headers=auth)

        # Query about breathing ranks the breathing entry first.
        results = await emb.search(db_session, "box breathing inhale hold exhale rhythm")
        assert results, "expected published chunks"
        assert results[0]["knowledge_id"] == breathing_id

        # Unpublish the breathing entry -> excluded from retrieval.
        await client.post(f"/api/admin/knowledge/{breathing_id}/unpublish", headers=auth)
        after = await emb.search(db_session, "box breathing inhale hold exhale rhythm")
        assert all(r["knowledge_id"] != breathing_id for r in after)

        # Re-publish -> re-embedded and retrievable again.
        await client.post(f"/api/admin/knowledge/{breathing_id}/publish", headers=auth)
        again = await emb.search(db_session, "box breathing inhale hold exhale rhythm")
        assert any(r["knowledge_id"] == breathing_id for r in again)
    finally:
        for i in ids:
            await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == i))
            await db_session.execute(delete(KnowledgeEntry).where(KnowledgeEntry.id == i))
        await db_session.commit()


async def test_search_respects_package_level(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    marker = uuid.uuid4().hex[:8]
    premium_id = await _create(
        client,
        auth,
        title=f"Advanced guide {marker}",
        body=f"Deep advanced energy practice guidance {marker} for experienced members.",
        min_ai_level="energy_guide",
    )
    pid = uuid.UUID(premium_id)
    try:
        await client.post(f"/api/admin/knowledge/{premium_id}/publish", headers=auth)
        q = f"advanced energy practice {marker}"

        # A basic-tier user cannot retrieve energy_guide content.
        basic = await emb.search(db_session, q, max_ai_level=AiLevel.basic_chat)
        assert all(r["knowledge_id"] != premium_id for r in basic)

        # A guide-tier user can.
        guide = await emb.search(db_session, q, max_ai_level=AiLevel.energy_guide)
        assert any(r["knowledge_id"] == premium_id for r in guide)
    finally:
        await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == pid))
        await db_session.execute(delete(KnowledgeEntry).where(KnowledgeEntry.id == pid))
        await db_session.commit()


def test_chunk_text_splits_paragraphs() -> None:
    chunks = emb.chunk_text("first para\n\nsecond para", max_chars=800)
    assert chunks == ["first para", "second para"]
    assert emb.chunk_text("   ") == []
