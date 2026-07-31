"""Agent rules service: CRUD ordered by priority."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rules import AgentRule
from app.schemas.rules import RuleCreate, RuleUpdate


async def list_rules(db: AsyncSession) -> Sequence[AgentRule]:
    # Lower priority number = evaluated first (safety overrides sit at the top).
    stmt = select(AgentRule).order_by(AgentRule.priority, AgentRule.created_at)
    return (await db.execute(stmt)).scalars().all()


async def get_rule(db: AsyncSession, rule_id: uuid.UUID) -> AgentRule | None:
    return await db.get(AgentRule, rule_id)


async def create_rule(db: AsyncSession, data: RuleCreate) -> AgentRule:
    rule = AgentRule(
        name=data.name,
        description=data.description,
        conditions=data.conditions.model_dump(exclude_none=True),
        actions=data.actions.model_dump(exclude_none=True),
        priority=data.priority,
        status=data.status,
        cooldown_seconds=data.cooldown_seconds,
        is_safety_override=data.is_safety_override,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


async def update_rule(db: AsyncSession, rule: AgentRule, data: RuleUpdate) -> AgentRule:
    fields = data.model_dump(exclude_unset=True)
    if "conditions" in fields and data.conditions is not None:
        rule.conditions = data.conditions.model_dump(exclude_none=True)
        fields.pop("conditions")
    if "actions" in fields and data.actions is not None:
        rule.actions = data.actions.model_dump(exclude_none=True)
        fields.pop("actions")
    for field, value in fields.items():
        setattr(rule, field, value)
    await db.flush()
    await db.refresh(rule)
    return rule


async def delete_rule(db: AsyncSession, rule: AgentRule) -> None:
    await db.delete(rule)
    await db.flush()
