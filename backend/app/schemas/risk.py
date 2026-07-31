"""Risk rule + blocked-claim schemas (Risk & Safety Manager)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskSeverity


class RiskRuleCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    keywords: list[str] = Field(default_factory=list)
    severity: RiskSeverity = RiskSeverity.medium
    fallback_action: dict[str, Any] | None = None
    is_active: bool = True


class RiskRuleUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=80)
    keywords: list[str] | None = None
    severity: RiskSeverity | None = None
    fallback_action: dict[str, Any] | None = None
    is_active: bool | None = None


class RiskRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category: str
    keywords: list[str]
    severity: RiskSeverity
    fallback_action: dict[str, Any] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BlockedClaimCreate(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class BlockedClaimUpdate(BaseModel):
    term: str | None = Field(default=None, min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class BlockedClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    term: str
    note: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
