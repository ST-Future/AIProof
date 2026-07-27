"""Knowledge base request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AiLevel, KnowledgeStatus


class KnowledgeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    category: str | None = Field(default=None, max_length=80)
    min_ai_level: AiLevel = AiLevel.none
    tags: list[str] = Field(default_factory=list)
    safety_notes: str | None = None
    # Optional initial status; content normally starts as a draft.
    status: KnowledgeStatus = KnowledgeStatus.draft


class KnowledgeUpdate(BaseModel):
    """Partial update of editable content fields only.

    Status is intentionally excluded — it changes via the publish / unpublish /
    retire actions so every transition is audited.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, max_length=80)
    min_ai_level: AiLevel | None = None
    tags: list[str] | None = None
    safety_notes: str | None = None


class KnowledgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    body: str
    category: str | None
    min_ai_level: AiLevel
    status: KnowledgeStatus
    tags: list[str]
    safety_notes: str | None
    created_at: datetime
    updated_at: datetime
