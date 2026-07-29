"""Admin routes for training stages and modules."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.training import TrainingModule, TrainingStage
from app.models.user import User
from app.schemas.training import (
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
    StageCreate,
    StageRead,
    StageUpdate,
)
from app.services import training as svc

stages_router = APIRouter(prefix="/api/admin/stages", tags=["admin:stages"])
modules_router = APIRouter(prefix="/api/admin/training-modules", tags=["admin:modules"])

_DUPLICATE = status.HTTP_409_CONFLICT
_NOT_FOUND = status.HTTP_404_NOT_FOUND


# --------------------------------- stages ---------------------------------


async def _stage_or_404(db: AsyncSession, stage_id: uuid.UUID) -> TrainingStage:
    stage = await svc.get_stage(db, stage_id)
    if stage is None:
        raise HTTPException(status_code=_NOT_FOUND, detail="Stage not found")
    return stage


@stages_router.get("", response_model=list[StageRead])
async def list_stages(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[TrainingStage]:
    return list(await svc.list_stages(db))


@stages_router.post("", response_model=StageRead, status_code=status.HTTP_201_CREATED)
async def create_stage(
    payload: StageCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingStage:
    try:
        stage = await svc.create_stage(db, payload)
    except svc.DuplicateKeyError as exc:
        raise HTTPException(status_code=_DUPLICATE, detail="Stage key already exists") from exc
    await db.commit()
    return stage


@stages_router.patch("/{stage_id}", response_model=StageRead)
async def update_stage(
    stage_id: uuid.UUID,
    payload: StageUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingStage:
    stage = await _stage_or_404(db, stage_id)
    stage = await svc.update_stage(db, stage, payload)
    await db.commit()
    return stage


@stages_router.delete("/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stage(
    stage_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    stage = await _stage_or_404(db, stage_id)
    await svc.delete_stage(db, stage)
    await db.commit()


# -------------------------------- modules ---------------------------------


async def _module_or_404(db: AsyncSession, module_id: uuid.UUID) -> TrainingModule:
    module = await svc.get_module(db, module_id)
    if module is None:
        raise HTTPException(status_code=_NOT_FOUND, detail="Module not found")
    return module


@modules_router.get("", response_model=list[ModuleRead])
async def list_modules(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[TrainingModule]:
    return list(await svc.list_modules(db))


@modules_router.post("", response_model=ModuleRead, status_code=status.HTTP_201_CREATED)
async def create_module(
    payload: ModuleCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingModule:
    try:
        module = await svc.create_module(db, payload)
    except svc.DuplicateKeyError as exc:
        raise HTTPException(status_code=_DUPLICATE, detail="Module key already exists") from exc
    await db.commit()
    return module


@modules_router.patch("/{module_id}", response_model=ModuleRead)
async def update_module(
    module_id: uuid.UUID,
    payload: ModuleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingModule:
    module = await _module_or_404(db, module_id)
    module = await svc.update_module(db, module, payload)
    await db.commit()
    return module


@modules_router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    module = await _module_or_404(db, module_id)
    await svc.delete_module(db, module)
    await db.commit()
