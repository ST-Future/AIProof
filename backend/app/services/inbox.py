"""Knowledge Inbox service: quick capture and promotion to a knowledge entry."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import InboxStatus, KnowledgeStatus
from app.models.knowledge import KnowledgeEntry, KnowledgeInboxItem
from app.schemas.inbox import InboxCreate, InboxPromote
from app.services.audit import record_admin_action


async def list_items(
    db: AsyncSession, *, status: InboxStatus | None = None
) -> Sequence[KnowledgeInboxItem]:
    stmt = select(KnowledgeInboxItem).order_by(KnowledgeInboxItem.created_at.desc())
    if status is not None:
        stmt = stmt.where(KnowledgeInboxItem.status == status)
    return (await db.execute(stmt)).scalars().all()


async def get_item(db: AsyncSession, item_id: uuid.UUID) -> KnowledgeInboxItem | None:
    return await db.get(KnowledgeInboxItem, item_id)


async def create_item(db: AsyncSession, data: InboxCreate) -> KnowledgeInboxItem:
    item = KnowledgeInboxItem(title=data.title, content=data.content, category=data.category)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def archive_item(
    db: AsyncSession, item: KnowledgeInboxItem, *, admin_id: uuid.UUID | None
) -> KnowledgeInboxItem:
    item.status = InboxStatus.archived
    await record_admin_action(
        db,
        admin_id=admin_id,
        action="knowledge_inbox.archive",
        entity_type="knowledge_inbox",
        entity_id=item.id,
    )
    await db.flush()
    await db.refresh(item)
    return item


def _derive_title(item: KnowledgeInboxItem, override: str | None) -> str:
    if override:
        return override
    if item.title:
        return item.title
    # Fall back to the first line of the note, trimmed.
    first_line = item.content.strip().splitlines()[0] if item.content.strip() else "Untitled note"
    return first_line[:200]


async def promote_item(
    db: AsyncSession,
    item: KnowledgeInboxItem,
    data: InboxPromote,
    *,
    admin_id: uuid.UUID | None,
) -> KnowledgeEntry:
    """Create a draft knowledge entry from the note and mark the note promoted."""
    entry = KnowledgeEntry(
        title=_derive_title(item, data.title),
        body=item.content,
        category=data.category or item.category,
        min_ai_level=data.min_ai_level,
        tags=data.tags,
        status=KnowledgeStatus.draft,
    )
    db.add(entry)
    await db.flush()  # assign entry.id

    item.status = InboxStatus.promoted
    item.promoted_entry_id = entry.id
    await record_admin_action(
        db,
        admin_id=admin_id,
        action="knowledge_inbox.promote",
        entity_type="knowledge_inbox",
        entity_id=item.id,
        detail={"entry_id": str(entry.id)},
    )
    await db.flush()
    await db.refresh(entry)
    return entry
