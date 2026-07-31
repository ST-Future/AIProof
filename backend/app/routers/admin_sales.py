"""Admin sales-trigger routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.rules import SalesTrigger
from app.models.user import User
from app.schemas.sales import SalesTriggerCreate, SalesTriggerRead, SalesTriggerUpdate
from app.services import sales as svc

router = APIRouter(prefix="/api/admin/sales-triggers", tags=["admin:sales"])


async def _or_404(db: AsyncSession, trigger_id: uuid.UUID) -> SalesTrigger:
    trigger = await svc.get_trigger(db, trigger_id)
    if trigger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales trigger not found")
    return trigger


@router.get("", response_model=list[SalesTriggerRead])
async def list_triggers(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[SalesTrigger]:
    return list(await svc.list_triggers(db))


@router.post("", response_model=SalesTriggerRead, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    payload: SalesTriggerCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SalesTrigger:
    trigger = await svc.create_trigger(db, payload)
    await db.commit()
    return trigger


@router.patch("/{trigger_id}", response_model=SalesTriggerRead)
async def update_trigger(
    trigger_id: uuid.UUID,
    payload: SalesTriggerUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SalesTrigger:
    trigger = await _or_404(db, trigger_id)
    trigger = await svc.update_trigger(db, trigger, payload)
    await db.commit()
    return trigger


@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trigger(
    trigger_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    trigger = await _or_404(db, trigger_id)
    await svc.delete_trigger(db, trigger)
    await db.commit()
