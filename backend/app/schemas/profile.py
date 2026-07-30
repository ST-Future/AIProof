"""Energy Profile + admin customer-summary schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AccessState, Package


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    summary: str | None
    traits: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class CustomerSummary(BaseModel):
    """One row in the admin Customers list — the customer's resolved state."""

    id: UUID
    email: str | None
    display_name: str | None
    created_at: datetime
    package: Package
    access_state: AccessState
    has_assessment: bool
    energy_summary: str | None
    stage: str | None
    day_count: int | None
    completed_sessions: int | None
