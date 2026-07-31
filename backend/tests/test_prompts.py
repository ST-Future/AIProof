"""Prompt versioning: create versions, publish flips active, rollback, audit."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.admin import AdminAction
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.rules import PromptVersion
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


async def test_prompt_publish_and_rollback(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    key = f"test.prompt.{uuid.uuid4().hex[:8]}"
    try:
        # Two versions for the same key; auto-incrementing version numbers.
        v1 = await client.post(
            "/api/admin/prompts", headers=auth, json={"key": key, "content": "v1 content"}
        )
        v2 = await client.post(
            "/api/admin/prompts", headers=auth, json={"key": key, "content": "v2 content"}
        )
        assert v1.json()["version"] == 1
        assert v2.json()["version"] == 2
        assert v1.json()["is_active"] is False and v2.json()["is_active"] is False
        v1_id, v2_id = v1.json()["id"], v2.json()["id"]

        pub = "/api/admin/prompts/publish"
        # Publish v1.
        pub1 = await client.post(pub, headers=auth, json={"version_id": v1_id})
        assert pub1.status_code == 200
        assert pub1.json()["is_active"] is True
        assert pub1.json()["status"] == "published"

        # Publish v2 -> active flips to v2, v1 archived + inactive.
        pub2 = await client.post(pub, headers=auth, json={"version_id": v2_id})
        assert pub2.json()["is_active"] is True

        def by_id(rows: list[dict], i: str) -> dict:
            return next(r for r in rows if r["id"] == i)

        rows = (await client.get("/api/admin/prompts", headers=auth)).json()
        assert by_id(rows, v2_id)["is_active"] is True
        assert by_id(rows, v1_id)["is_active"] is False
        assert by_id(rows, v1_id)["status"] == "archived"

        # Rollback -> active flips back to v1.
        rb = await client.post("/api/admin/prompts/rollback", headers=auth, json={"key": key})
        assert rb.status_code == 200
        assert rb.json()["id"] == v1_id
        assert rb.json()["is_active"] is True

        rows2 = (await client.get("/api/admin/prompts", headers=auth)).json()
        assert by_id(rows2, v1_id)["is_active"] is True
        assert by_id(rows2, v2_id)["is_active"] is False

        # Publish + rollback are auditable.
        actions = {
            a.action
            for a in (
                await db_session.execute(
                    select(AdminAction).where(
                        AdminAction.entity_id.in_([uuid.UUID(v1_id), uuid.UUID(v2_id)])
                    )
                )
            )
            .scalars()
            .all()
        }
        assert "prompt.publish" in actions
        assert "prompt.rollback" in actions
    finally:
        ids = [
            r["id"]
            for r in (await client.get("/api/admin/prompts", headers=auth)).json()
            if r["key"] == key
        ]
        for i in ids:
            iid = uuid.UUID(i)
            await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == iid))
            await db_session.execute(delete(PromptVersion).where(PromptVersion.id == iid))
        await db_session.commit()


async def test_rollback_without_target_400(client: AsyncClient, db_session: AsyncSession) -> None:
    auth = await _admin_headers(db_session)
    key = f"test.single.{uuid.uuid4().hex[:8]}"
    created = await client.post(
        "/api/admin/prompts", headers=auth, json={"key": key, "content": "only"}
    )
    pid = created.json()["id"]
    try:
        await client.post("/api/admin/prompts/publish", headers=auth, json={"version_id": pid})
        # Only one version exists -> nothing to roll back to.
        rb = await client.post("/api/admin/prompts/rollback", headers=auth, json={"key": key})
        assert rb.status_code == 400
    finally:
        await db_session.execute(delete(AdminAction).where(AdminAction.entity_id == uuid.UUID(pid)))
        await db_session.execute(delete(PromptVersion).where(PromptVersion.id == uuid.UUID(pid)))
        await db_session.commit()


async def test_prompts_require_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/admin/prompts")).status_code == 401
