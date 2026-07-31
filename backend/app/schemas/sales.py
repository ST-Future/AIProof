"""Sales trigger schemas — when package explanation/upsell is allowed or blocked."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Package, RuleStatus, SalesTriggerMode
from app.schemas.rules import RuleConditions


class SalesTriggerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    conditions: RuleConditions
    target_package: Package | None = None
    mode: SalesTriggerMode = SalesTriggerMode.allow
    priority: int = 100
    status: RuleStatus = RuleStatus.draft
    cooldown_seconds: int | None = Field(default=None, ge=0)


class SalesTriggerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    conditions: RuleConditions | None = None
    target_package: Package | None = None
    mode: SalesTriggerMode | None = None
    priority: int | None = None
    status: RuleStatus | None = None
    cooldown_seconds: int | None = Field(default=None, ge=0)


class SalesTriggerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    conditions: dict[str, Any]
    target_package: Package | None
    mode: SalesTriggerMode
    priority: int
    status: RuleStatus
    cooldown_seconds: int | None
    created_at: datetime
    updated_at: datetime
