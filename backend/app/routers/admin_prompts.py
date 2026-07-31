"""Admin prompt-versioning routes (create versions, publish, rollback)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.rules import PromptVersion
from app.models.user import User
from app.schemas.prompts import (
    PromptCreate,
    PromptRead,
    PromptUpdate,
    PublishRequest,
    RollbackRequest,
)
from app.services import prompts as svc

router = APIRouter(prefix="/api/admin/prompts", tags=["admin:prompts"])


async def _or_404(db: AsyncSession, prompt_id: uuid.UUID) -> PromptVersion:
    prompt = await svc.get_prompt(db, prompt_id)
    if prompt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return prompt


@router.get("", response_model=list[PromptRead])
async def list_prompts(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[PromptVersion]:
    return list(await svc.list_prompts(db))


@router.post("", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    payload: PromptCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PromptVersion:
    prompt = await svc.create_prompt(db, payload)
    await db.commit()
    return prompt


@router.patch("/{prompt_id}", response_model=PromptRead)
async def update_prompt(
    prompt_id: uuid.UUID,
    payload: PromptUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PromptVersion:
    prompt = await _or_404(db, prompt_id)
    prompt = await svc.update_prompt(db, prompt, payload)
    await db.commit()
    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    prompt = await _or_404(db, prompt_id)
    if prompt.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cannot delete the active version"
        )
    await svc.delete_prompt(db, prompt)
    await db.commit()


@router.post("/publish", response_model=PromptRead)
async def publish_prompt(
    payload: PublishRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PromptVersion:
    prompt = await _or_404(db, payload.version_id)
    prompt = await svc.publish(db, prompt, admin_id=admin.id)
    await db.commit()
    return prompt


@router.post("/rollback", response_model=PromptRead)
async def rollback_prompt(
    payload: RollbackRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PromptVersion:
    try:
        prompt = await svc.rollback(db, payload.key, admin_id=admin.id)
    except svc.NoRollbackTargetError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No previous version to roll back to",
        ) from exc
    await db.commit()
    return prompt
