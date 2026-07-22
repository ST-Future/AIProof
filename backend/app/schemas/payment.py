"""Pydantic schemas for payment records."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import Package, PaymentProvider, PaymentStatus


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: PaymentProvider
    package: Package
    status: PaymentStatus
    amount: Decimal
    currency: str
    external_id: str | None
    tx_hash: str | None
    created_at: datetime
