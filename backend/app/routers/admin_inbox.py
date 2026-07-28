"""Admin Knowledge Inbox routes: quick capture + promote to a knowledge entry."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.enums import InboxStatus
from app.models.knowledge import KnowledgeEntry, KnowledgeInboxItem
from app.models.user import User
from app.schemas.inbox import InboxCreate, InboxPromote, InboxRead
from app.schemas.knowledge import KnowledgeRead
from app.services import inbox as svc

router = APIRouter(prefix="/api/admin/inbox", tags=["admin:inbox"])


async def _get_or_404(db: AsyncSession, item_id: uuid.UUID) -> KnowledgeInboxItem:
    item = await svc.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inbox item not found")
    return item


@router.get("", response_model=list[InboxRead])
async def list_inbox(
    status_filter: InboxStatus | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeInboxItem]:
    return list(await svc.list_items(db, status=status_filter))


@router.post("", response_model=InboxRead, status_code=status.HTTP_201_CREATED)
async def create_inbox(
    payload: InboxCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeInboxItem:
    item = await svc.create_item(db, payload)
    await db.commit()
    return item


@router.post("/{item_id}/promote", response_model=KnowledgeRead)
async def promote_inbox(
    item_id: uuid.UUID,
    payload: InboxPromote,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    item = await _get_or_404(db, item_id)
    if item.status is InboxStatus.promoted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Note already promoted")
    entry = await svc.promote_item(db, item, payload, admin_id=admin.id)
    await db.commit()
    return entry


@router.post("/{item_id}/archive", response_model=InboxRead)
async def archive_inbox(
    item_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeInboxItem:
    item = await _get_or_404(db, item_id)
    item = await svc.archive_item(db, item, admin_id=admin.id)
    await db.commit()
    return item
