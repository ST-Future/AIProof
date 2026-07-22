"""Pydantic schemas for memberships."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AccessState, AiLevel, Package, RenewalStatus


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    package: Package
    access_state: AccessState
    ai_level: AiLevel
    renewal_status: RenewalStatus
    current_period_start: datetime | None
    expires_at: datetime | None
