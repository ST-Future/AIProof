"""Risk & Safety service: risk_rules + blocked_claims CRUD."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rules import BlockedClaim, RiskRule
from app.schemas.risk import (
    BlockedClaimCreate,
    BlockedClaimUpdate,
    RiskRuleCreate,
    RiskRuleUpdate,
)


class DuplicateTermError(Exception):
    """Raised when adding a blocked-claim term that already exists."""


# ------------------------------- risk rules -------------------------------


async def list_risk_rules(db: AsyncSession) -> Sequence[RiskRule]:
    stmt = select(RiskRule).order_by(RiskRule.category)
    return (await db.execute(stmt)).scalars().all()


async def get_risk_rule(db: AsyncSession, rule_id: uuid.UUID) -> RiskRule | None:
    return await db.get(RiskRule, rule_id)


async def create_risk_rule(db: AsyncSession, data: RiskRuleCreate) -> RiskRule:
    rule = RiskRule(**data.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


async def update_risk_rule(db: AsyncSession, rule: RiskRule, data: RiskRuleUpdate) -> RiskRule:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.flush()
    await db.refresh(rule)
    return rule


async def delete_risk_rule(db: AsyncSession, rule: RiskRule) -> None:
    await db.delete(rule)
    await db.flush()


# ----------------------------- blocked claims -----------------------------


async def list_blocked_claims(db: AsyncSession) -> Sequence[BlockedClaim]:
    stmt = select(BlockedClaim).order_by(BlockedClaim.term)
    return (await db.execute(stmt)).scalars().all()


async def get_blocked_claim(db: AsyncSession, claim_id: uuid.UUID) -> BlockedClaim | None:
    return await db.get(BlockedClaim, claim_id)


async def create_blocked_claim(db: AsyncSession, data: BlockedClaimCreate) -> BlockedClaim:
    exists = (
        await db.execute(select(BlockedClaim.id).where(BlockedClaim.term == data.term))
    ).first()
    if exists:
        raise DuplicateTermError(data.term)
    claim = BlockedClaim(**data.model_dump())
    db.add(claim)
    await db.flush()
    await db.refresh(claim)
    return claim


async def update_blocked_claim(
    db: AsyncSession, claim: BlockedClaim, data: BlockedClaimUpdate
) -> BlockedClaim:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(claim, field, value)
    await db.flush()
    await db.refresh(claim)
    return claim


async def delete_blocked_claim(db: AsyncSession, claim: BlockedClaim) -> None:
    await db.delete(claim)
    await db.flush()
