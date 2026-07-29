"""Training service: CRUD for stages and modules."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training import TrainingModule, TrainingStage
from app.schemas.training import ModuleCreate, ModuleUpdate, StageCreate, StageUpdate


class DuplicateKeyError(Exception):
    """Raised when creating a stage/module with an already-used key."""


# --------------------------------- stages ---------------------------------


async def list_stages(db: AsyncSession) -> Sequence[TrainingStage]:
    stmt = select(TrainingStage).order_by(TrainingStage.order_index, TrainingStage.name)
    return (await db.execute(stmt)).scalars().all()


async def get_stage(db: AsyncSession, stage_id: uuid.UUID) -> TrainingStage | None:
    return await db.get(TrainingStage, stage_id)


async def _stage_key_exists(db: AsyncSession, key: str) -> bool:
    return (
        await db.execute(select(TrainingStage.id).where(TrainingStage.key == key))
    ).first() is not None


async def create_stage(db: AsyncSession, data: StageCreate) -> TrainingStage:
    if await _stage_key_exists(db, data.key):
        raise DuplicateKeyError(data.key)
    stage = TrainingStage(**data.model_dump())
    db.add(stage)
    await db.flush()
    await db.refresh(stage)
    return stage


async def update_stage(db: AsyncSession, stage: TrainingStage, data: StageUpdate) -> TrainingStage:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(stage, field, value)
    await db.flush()
    await db.refresh(stage)
    return stage


async def delete_stage(db: AsyncSession, stage: TrainingStage) -> None:
    await db.delete(stage)
    await db.flush()


# -------------------------------- modules ---------------------------------


async def list_modules(db: AsyncSession) -> Sequence[TrainingModule]:
    stmt = select(TrainingModule).order_by(TrainingModule.order_index, TrainingModule.name)
    return (await db.execute(stmt)).scalars().all()


async def get_module(db: AsyncSession, module_id: uuid.UUID) -> TrainingModule | None:
    return await db.get(TrainingModule, module_id)


async def _module_key_exists(db: AsyncSession, key: str) -> bool:
    return (
        await db.execute(select(TrainingModule.id).where(TrainingModule.key == key))
    ).first() is not None


async def create_module(db: AsyncSession, data: ModuleCreate) -> TrainingModule:
    if await _module_key_exists(db, data.key):
        raise DuplicateKeyError(data.key)
    module = TrainingModule(**data.model_dump())
    db.add(module)
    await db.flush()
    await db.refresh(module)
    return module


async def update_module(
    db: AsyncSession, module: TrainingModule, data: ModuleUpdate
) -> TrainingModule:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(module, field, value)
    await db.flush()
    await db.refresh(module)
    return module


async def delete_module(db: AsyncSession, module: TrainingModule) -> None:
    await db.delete(module)
    await db.flush()
