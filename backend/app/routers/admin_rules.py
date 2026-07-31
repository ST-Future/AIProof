"""Admin agent-rules routes (structured IF/THEN decision rules)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.rules import AgentRule
from app.models.user import User
from app.schemas.rules import RuleCreate, RuleRead, RuleUpdate
from app.services import rules as svc

router = APIRouter(prefix="/api/admin/rules", tags=["admin:rules"])


async def _rule_or_404(db: AsyncSession, rule_id: uuid.UUID) -> AgentRule:
    rule = await svc.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.get("", response_model=list[RuleRead])
async def list_rules(
    _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> list[AgentRule]:
    return list(await svc.list_rules(db))


@router.post("", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: RuleCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AgentRule:
    rule = await svc.create_rule(db, payload)
    await db.commit()
    return rule


@router.patch("/{rule_id}", response_model=RuleRead)
async def update_rule(
    rule_id: uuid.UUID,
    payload: RuleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AgentRule:
    rule = await _rule_or_404(db, rule_id)
    rule = await svc.update_rule(db, rule, payload)
    await db.commit()
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    rule = await _rule_or_404(db, rule_id)
    await svc.delete_rule(db, rule)
    await db.commit()
