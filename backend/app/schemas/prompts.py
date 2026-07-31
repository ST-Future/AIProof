"""Prompt version schemas.

Prompts are grouped by ``key`` (e.g. "system.base", or a stage/AI-level key).
Each key has many versions; exactly one is active (published) at a time.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PromptStatus


class PromptCreate(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    notes: str | None = None


class PromptUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)
    notes: str | None = None


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    version: int
    content: str
    status: PromptStatus
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PublishRequest(BaseModel):
    version_id: UUID


class RollbackRequest(BaseModel):
    key: str
