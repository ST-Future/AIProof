"""Sales trigger service: CRUD ordered by priority."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rules import SalesTrigger
from app.schemas.sales import SalesTriggerCreate, SalesTriggerUpdate


async def list_triggers(db: AsyncSession) -> Sequence[SalesTrigger]:
    stmt = select(SalesTrigger).order_by(SalesTrigger.priority, SalesTrigger.created_at)
    return (await db.execute(stmt)).scalars().all()


async def get_trigger(db: AsyncSession, trigger_id: uuid.UUID) -> SalesTrigger | None:
    return await db.get(SalesTrigger, trigger_id)


async def create_trigger(db: AsyncSession, data: SalesTriggerCreate) -> SalesTrigger:
    trigger = SalesTrigger(
        name=data.name,
        description=data.description,
        conditions=data.conditions.model_dump(exclude_none=True),
        target_package=data.target_package,
        mode=data.mode,
        priority=data.priority,
        status=data.status,
        cooldown_seconds=data.cooldown_seconds,
    )
    db.add(trigger)
    await db.flush()
    await db.refresh(trigger)
    return trigger


async def update_trigger(
    db: AsyncSession, trigger: SalesTrigger, data: SalesTriggerUpdate
) -> SalesTrigger:
    fields = data.model_dump(exclude_unset=True)
    if "conditions" in fields and data.conditions is not None:
        trigger.conditions = data.conditions.model_dump(exclude_none=True)
        fields.pop("conditions")
    for field, value in fields.items():
        setattr(trigger, field, value)
    await db.flush()
    await db.refresh(trigger)
    return trigger


async def delete_trigger(db: AsyncSession, trigger: SalesTrigger) -> None:
    await db.delete(trigger)
    await db.flush()
