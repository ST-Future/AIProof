"""Agent rule schemas.

Conditions and actions are **structured JSON** with documented, known fields
(plus room for extras), not free text — so the rules engine can evaluate them.

Conditions (all optional; a rule matches when every present condition holds):
  stages                  list[str]  — training stage keys
  intents                 list[str]  — recognized intents (e.g. price_question)
  risks                   list[str]  — risk categories (e.g. cardiac)
  min_completed_sessions  int        — user has completed >= N sessions
  max_completed_sessions  int        — user has completed <= N sessions
  min_day_count           int        — user is on day >= N

Actions:
  type            str   — e.g. continue_basics | safety_first | allow_sales
                          | start_cooldown | pause_access | recommend_next
  disable_sales   bool  — suppress any upsell
  allow_sales     bool  — permit package explanation / upsell
  lower_difficulty bool — ease the current practice
  cooldown_seconds int  — sales cooldown to apply
  message_hint    str   — guidance for the AI generation step
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RuleStatus


class RuleConditions(BaseModel):
    model_config = ConfigDict(extra="allow")

    stages: list[str] | None = None
    intents: list[str] | None = None
    risks: list[str] | None = None
    min_completed_sessions: int | None = None
    max_completed_sessions: int | None = None
    min_day_count: int | None = None


class RuleActions(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = Field(min_length=1)
    disable_sales: bool | None = None
    allow_sales: bool | None = None
    lower_difficulty: bool | None = None
    cooldown_seconds: int | None = None
    message_hint: str | None = None


class RuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    conditions: RuleConditions
    actions: RuleActions
    priority: int = 100
    status: RuleStatus = RuleStatus.draft
    cooldown_seconds: int | None = Field(default=None, ge=0)
    is_safety_override: bool = False


class RuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    conditions: RuleConditions | None = None
    actions: RuleActions | None = None
    priority: int | None = None
    status: RuleStatus | None = None
    cooldown_seconds: int | None = Field(default=None, ge=0)
    is_safety_override: bool | None = None


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    conditions: dict[str, Any]
    actions: dict[str, Any]
    priority: int
    status: RuleStatus
    cooldown_seconds: int | None
    is_safety_override: bool
    created_at: datetime
    updated_at: datetime
