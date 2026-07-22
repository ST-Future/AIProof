"""Membership model — the current access state for a user.

One row per user, representing their *current* package and access. Payment
history lives in ``payment_records``; this table is the resolved state the
Agent runtime and access checks read from.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import AccessState, AiLevel, Package, RenewalStatus

if TYPE_CHECKING:
    from app.models.user import User


class Membership(TimestampMixin, Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    package: Mapped[Package] = mapped_column(
        SAEnum(Package, native_enum=False, length=20),
        default=Package.none,
        nullable=False,
    )
    access_state: Mapped[AccessState] = mapped_column(
        SAEnum(AccessState, native_enum=False, length=20),
        default=AccessState.inactive,
        nullable=False,
    )
    ai_level: Mapped[AiLevel] = mapped_column(
        SAEnum(AiLevel, native_enum=False, length=20),
        default=AiLevel.none,
        nullable=False,
    )
    renewal_status: Mapped[RenewalStatus] = mapped_column(
        SAEnum(RenewalStatus, native_enum=False, length=20),
        default=RenewalStatus.none,
        nullable=False,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # For crypto: start + 30 days. For Stripe/PayPal: current period end.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="membership")
