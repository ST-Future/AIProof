"""Training stage and module request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AiLevel

# --------------------------------- stages ---------------------------------


class StageCreate(BaseModel):
    key: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    order_index: int = 0
    entry_conditions: dict[str, Any] | None = None
    is_active: bool = True


class StageUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    order_index: int | None = None
    entry_conditions: dict[str, Any] | None = None
    is_active: bool | None = None


class StageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    name: str
    description: str | None
    order_index: int
    entry_conditions: dict[str, Any] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# -------------------------------- modules ---------------------------------


class ModuleCreate(BaseModel):
    key: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=120)
    target_user: str | None = Field(default=None, max_length=160)
    stage_id: UUID | None = None
    goal: str | None = None
    steps: list[str] = Field(default_factory=list)
    duration_minutes: int | None = Field(default=None, ge=0)
    stop_conditions: dict[str, Any] | None = None
    next_module_id: UUID | None = None
    next_stage_id: UUID | None = None
    min_ai_level: AiLevel = AiLevel.none
    order_index: int = 0
    is_active: bool = True


class ModuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_user: str | None = Field(default=None, max_length=160)
    stage_id: UUID | None = None
    goal: str | None = None
    steps: list[str] | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    stop_conditions: dict[str, Any] | None = None
    next_module_id: UUID | None = None
    next_stage_id: UUID | None = None
    min_ai_level: AiLevel | None = None
    order_index: int | None = None
    is_active: bool | None = None


class ModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    name: str
    target_user: str | None
    stage_id: UUID | None
    goal: str | None
    steps: list[str]
    duration_minutes: int | None
    stop_conditions: dict[str, Any] | None
    next_module_id: UUID | None
    next_stage_id: UUID | None
    min_ai_level: AiLevel
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
