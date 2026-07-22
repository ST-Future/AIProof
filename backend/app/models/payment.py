"""Payment record model — one row per payment attempt/event.

Covers Stripe, PayPal, and BNB Smart Chain crypto (USDT/USDC). The raw
provider/webhook payload is retained for auditing and reconciliation.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import Package, PaymentProvider, PaymentStatus

if TYPE_CHECKING:
    from app.models.user import User


class PaymentRecord(TimestampMixin, Base):
    __tablename__ = "payment_records"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provider: Mapped[PaymentProvider] = mapped_column(
        SAEnum(PaymentProvider, native_enum=False, length=20), nullable=False
    )
    package: Mapped[Package] = mapped_column(
        SAEnum(Package, native_enum=False, length=20), nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, native_enum=False, length=20),
        default=PaymentStatus.pending,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    # Stripe/PayPal object id (idempotency); null for crypto.
    external_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    # Crypto transaction hash + chain; null for card/PayPal.
    tx_hash: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    chain: Mapped[str | None] = mapped_column(String(30), nullable=True)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped[User] = relationship(back_populates="payments")
