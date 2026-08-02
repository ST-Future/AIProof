"""Admin knowledge base routes (CRUD + audited status transitions)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.enums import KnowledgeStatus
from app.models.knowledge import KnowledgeEntry
from app.models.user import User
from app.schemas.knowledge import KnowledgeCreate, KnowledgeRead, KnowledgeUpdate
from app.services import embeddings as emb_svc
from app.services import knowledge as svc

router = APIRouter(prefix="/api/admin/knowledge", tags=["admin:knowledge"])


async def _get_or_404(db: AsyncSession, entry_id: uuid.UUID) -> KnowledgeEntry:
    entry = await svc.get_entry(db, entry_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge entry not found"
        )
    return entry


@router.get("", response_model=list[KnowledgeRead])
async def list_knowledge(
    status_filter: KnowledgeStatus | None = None,
    category: str | None = None,
    q: str | None = None,
    tag: str | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeEntry]:
    return list(
        await svc.list_entries(db, status=status_filter, category=category, query=q, tag=tag)
    )


@router.post("", response_model=KnowledgeRead, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    payload: KnowledgeCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    entry = await svc.create_entry(db, payload)
    await db.commit()
    return entry


@router.get("/{entry_id}", response_model=KnowledgeRead)
async def get_knowledge(
    entry_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    return await _get_or_404(db, entry_id)


@router.patch("/{entry_id}", response_model=KnowledgeRead)
async def update_knowledge(
    entry_id: uuid.UUID,
    payload: KnowledgeUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    entry = await _get_or_404(db, entry_id)
    entry = await svc.update_entry(db, entry, payload)
    await db.commit()
    return entry


async def _transition(
    db: AsyncSession,
    entry_id: uuid.UUID,
    new_status: KnowledgeStatus,
    action: str,
    admin: User,
) -> KnowledgeEntry:
    entry = await _get_or_404(db, entry_id)
    entry = await svc.set_status(db, entry, new_status, admin_id=admin.id, action=action)
    # Keep the RAG index in sync: publish (re)embeds; unpublish/retire removes it.
    if new_status is KnowledgeStatus.published:
        await emb_svc.embed_knowledge_entry(db, entry)
    else:
        await emb_svc.delete_entry_embeddings(db, entry.id)
    await db.commit()
    return entry


@router.post("/{entry_id}/publish", response_model=KnowledgeRead)
async def publish_knowledge(
    entry_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    return await _transition(db, entry_id, KnowledgeStatus.published, "knowledge.publish", admin)


@router.post("/{entry_id}/unpublish", response_model=KnowledgeRead)
async def unpublish_knowledge(
    entry_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    return await _transition(
        db, entry_id, KnowledgeStatus.unpublished, "knowledge.unpublish", admin
    )


@router.post("/{entry_id}/retire", response_model=KnowledgeRead)
async def retire_knowledge(
    entry_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeEntry:
    return await _transition(db, entry_id, KnowledgeStatus.retired, "knowledge.retire", admin)
