"""User account and identity models.

A ``User`` is the core account. Login methods (email + password, wallet
address) live in ``UserIdentity`` rows, which is what makes email↔wallet
account linking possible: one user can own several identities.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import AccountStatus, IdentityProvider, UserRole


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False, length=20),
        default=UserRole.customer,
        nullable=False,
    )
    status: Mapped[AccountStatus] = mapped_column(
        SAEnum(AccountStatus, native_enum=False, length=20),
        default=AccountStatus.active,
        nullable=False,
    )
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    identities: Mapped[list[UserIdentity]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    membership: Mapped[Membership | None] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    payments: Mapped[list[PaymentRecord]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserIdentity(TimestampMixin, Base):
    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint("provider", "identifier", name="uq_identity_provider_identifier"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provider: Mapped[IdentityProvider] = mapped_column(
        SAEnum(IdentityProvider, native_enum=False, length=20), nullable=False
    )
    # Normalized email (lowercased) or checksummed wallet address.
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    # bcrypt hash — set for email identities only, null for wallet.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="identities")


# Imported at module end to avoid circular imports at definition time while
# still resolving the string-based relationship targets above.
from app.models.membership import Membership  # noqa: E402
from app.models.payment import PaymentRecord  # noqa: E402
