"""Admin Risk & Safety routes: risk rules + blocked-claims word list."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.rules import BlockedClaim, RiskRule
from app.models.user import User
from app.schemas.risk import (
    BlockedClaimCreate,
    BlockedClaimRead,
    BlockedClaimUpdate,
    RiskRuleCreate,
    RiskRuleRead,
    RiskRuleUpdate,
)
from app.services import risk as svc

risk_router = APIRouter(prefix="/api/admin/risk-rules", tags=["admin:risk"])
claims_router = APIRouter(prefix="/api/admin/blocked-claims", tags=["admin:risk"])

_NOT_FOUND = status.HTTP_404_NOT_FOUND


# ------------------------------- risk rules -------------------------------


async def _rule_or_404(db: AsyncSession, rule_id: uuid.UUID) -> RiskRule:
    rule = await svc.get_risk_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=_NOT_FOUND, detail="Risk rule not found")
    return rule


@risk_router.get("", response_model=list[RiskRuleRead])
async def list_risk_rules(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[RiskRule]:
    return list(await svc.list_risk_rules(db))


@risk_router.post("", response_model=RiskRuleRead, status_code=status.HTTP_201_CREATED)
async def create_risk_rule(
    payload: RiskRuleCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> RiskRule:
    rule = await svc.create_risk_rule(db, payload)
    await db.commit()
    return rule


@risk_router.patch("/{rule_id}", response_model=RiskRuleRead)
async def update_risk_rule(
    rule_id: uuid.UUID,
    payload: RiskRuleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> RiskRule:
    rule = await _rule_or_404(db, rule_id)
    rule = await svc.update_risk_rule(db, rule, payload)
    await db.commit()
    return rule


@risk_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk_rule(
    rule_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    rule = await _rule_or_404(db, rule_id)
    await svc.delete_risk_rule(db, rule)
    await db.commit()


# ----------------------------- blocked claims -----------------------------


async def _claim_or_404(db: AsyncSession, claim_id: uuid.UUID) -> BlockedClaim:
    claim = await svc.get_blocked_claim(db, claim_id)
    if claim is None:
        raise HTTPException(status_code=_NOT_FOUND, detail="Blocked claim not found")
    return claim


@claims_router.get("", response_model=list[BlockedClaimRead])
async def list_blocked_claims(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[BlockedClaim]:
    return list(await svc.list_blocked_claims(db))


@claims_router.post("", response_model=BlockedClaimRead, status_code=status.HTTP_201_CREATED)
async def create_blocked_claim(
    payload: BlockedClaimCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlockedClaim:
    try:
        claim = await svc.create_blocked_claim(db, payload)
    except svc.DuplicateTermError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Term already blocked"
        ) from exc
    await db.commit()
    return claim


@claims_router.patch("/{claim_id}", response_model=BlockedClaimRead)
async def update_blocked_claim(
    claim_id: uuid.UUID,
    payload: BlockedClaimUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlockedClaim:
    claim = await _claim_or_404(db, claim_id)
    claim = await svc.update_blocked_claim(db, claim, payload)
    await db.commit()
    return claim


@claims_router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocked_claim(
    claim_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    claim = await _claim_or_404(db, claim_id)
    await svc.delete_blocked_claim(db, claim)
    await db.commit()
