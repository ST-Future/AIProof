"""Knowledge Inbox request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AiLevel, InboxStatus


class InboxCreate(BaseModel):
    content: str = Field(min_length=1)
    title: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=80)


class InboxRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    content: str
    category: str | None
    status: InboxStatus
    promoted_entry_id: UUID | None
    created_at: datetime
    updated_at: datetime


class InboxPromote(BaseModel):
    """Overrides applied when promoting a note into a knowledge entry.

    Anything omitted falls back to the inbox item's own values.
    """

    title: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=80)
    min_ai_level: AiLevel = AiLevel.none
    tags: list[str] = Field(default_factory=list)
