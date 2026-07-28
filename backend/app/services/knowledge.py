"""Knowledge base service: CRUD and audited status transitions."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import KnowledgeStatus
from app.models.knowledge import KnowledgeEntry
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from app.services.audit import record_admin_action


async def list_entries(
    db: AsyncSession,
    *,
    status: KnowledgeStatus | None = None,
    category: str | None = None,
    query: str | None = None,
    tag: str | None = None,
) -> Sequence[KnowledgeEntry]:
    stmt = select(KnowledgeEntry).order_by(KnowledgeEntry.updated_at.desc())
    if status is not None:
        stmt = stmt.where(KnowledgeEntry.status == status)
    if category:
        stmt = stmt.where(KnowledgeEntry.category == category)
    if query:
        pattern = f"%{query}%"
        stmt = stmt.where(KnowledgeEntry.title.ilike(pattern) | KnowledgeEntry.body.ilike(pattern))
    if tag:
        # JSONB array contains the given tag.
        stmt = stmt.where(KnowledgeEntry.tags.contains([tag]))
    return (await db.execute(stmt)).scalars().all()


async def get_entry(db: AsyncSession, entry_id: uuid.UUID) -> KnowledgeEntry | None:
    return await db.get(KnowledgeEntry, entry_id)


async def create_entry(db: AsyncSession, data: KnowledgeCreate) -> KnowledgeEntry:
    entry = KnowledgeEntry(
        title=data.title,
        body=data.body,
        category=data.category,
        min_ai_level=data.min_ai_level,
        tags=data.tags,
        safety_notes=data.safety_notes,
        status=data.status,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def update_entry(
    db: AsyncSession, entry: KnowledgeEntry, data: KnowledgeUpdate
) -> KnowledgeEntry:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.flush()
    await db.refresh(entry)
    return entry


async def set_status(
    db: AsyncSession,
    entry: KnowledgeEntry,
    new_status: KnowledgeStatus,
    *,
    admin_id: uuid.UUID | None,
    action: str,
) -> KnowledgeEntry:
    previous = entry.status
    entry.status = new_status
    await record_admin_action(
        db,
        admin_id=admin_id,
        action=action,
        entity_type="knowledge_entry",
        entity_id=entry.id,
        detail={"from": previous.value, "to": new_status.value},
    )
    await db.flush()
    await db.refresh(entry)
    return entry
