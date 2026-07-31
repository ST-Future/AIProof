"""Prompt versioning service: create versions, publish, rollback (audited)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromptStatus
from app.models.rules import PromptVersion
from app.schemas.prompts import PromptCreate, PromptUpdate
from app.services.audit import record_admin_action


class NoRollbackTargetError(Exception):
    """Raised when there is no previous version to roll back to for a key."""


async def list_prompts(db: AsyncSession) -> Sequence[PromptVersion]:
    stmt = select(PromptVersion).order_by(PromptVersion.key, PromptVersion.version.desc())
    return (await db.execute(stmt)).scalars().all()


async def get_prompt(db: AsyncSession, prompt_id: uuid.UUID) -> PromptVersion | None:
    return await db.get(PromptVersion, prompt_id)


async def _next_version(db: AsyncSession, key: str) -> int:
    current = (
        await db.execute(select(func.max(PromptVersion.version)).where(PromptVersion.key == key))
    ).scalar_one_or_none()
    return (current or 0) + 1


async def create_prompt(db: AsyncSession, data: PromptCreate) -> PromptVersion:
    prompt = PromptVersion(
        key=data.key,
        version=await _next_version(db, data.key),
        content=data.content,
        notes=data.notes,
        status=PromptStatus.draft,
        is_active=False,
    )
    db.add(prompt)
    await db.flush()
    await db.refresh(prompt)
    return prompt


async def update_prompt(
    db: AsyncSession, prompt: PromptVersion, data: PromptUpdate
) -> PromptVersion:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prompt, field, value)
    await db.flush()
    await db.refresh(prompt)
    return prompt


async def delete_prompt(db: AsyncSession, prompt: PromptVersion) -> None:
    await db.delete(prompt)
    await db.flush()


async def _activate(
    db: AsyncSession,
    prompt: PromptVersion,
    *,
    admin_id: uuid.UUID | None,
    action: str,
    detail: dict[str, object],
) -> PromptVersion:
    """Make ``prompt`` the single active/published version for its key."""
    others = (
        (await db.execute(select(PromptVersion).where(PromptVersion.key == prompt.key)))
        .scalars()
        .all()
    )
    for other in others:
        if other.id == prompt.id:
            continue
        if other.is_active:
            other.status = PromptStatus.archived
        other.is_active = False

    prompt.is_active = True
    prompt.status = PromptStatus.published

    await record_admin_action(
        db,
        admin_id=admin_id,
        action=action,
        entity_type="prompt_version",
        entity_id=prompt.id,
        detail=detail,
    )
    await db.flush()
    await db.refresh(prompt)
    return prompt


async def publish(
    db: AsyncSession, prompt: PromptVersion, *, admin_id: uuid.UUID | None
) -> PromptVersion:
    return await _activate(
        db,
        prompt,
        admin_id=admin_id,
        action="prompt.publish",
        detail={"key": prompt.key, "version": prompt.version},
    )


async def rollback(db: AsyncSession, key: str, *, admin_id: uuid.UUID | None) -> PromptVersion:
    """Re-activate the most recent previous version for ``key``."""
    versions = (
        (
            await db.execute(
                select(PromptVersion)
                .where(PromptVersion.key == key)
                .order_by(PromptVersion.version.desc())
            )
        )
        .scalars()
        .all()
    )
    active = next((v for v in versions if v.is_active), None)
    # The target is the highest-version version that is not currently active.
    target = next((v for v in versions if not v.is_active), None)
    if target is None:
        raise NoRollbackTargetError(key)

    return await _activate(
        db,
        target,
        admin_id=admin_id,
        action="prompt.rollback",
        detail={
            "key": key,
            "from_version": active.version if active else None,
            "to_version": target.version,
        },
    )
