"""Integration test: create a user with identity, membership, and payment.

Exercises the backend DB layer end-to-end against the running Postgres.
The ``db_session`` fixture rolls back afterwards, so the dev DB stays clean.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    AccessState,
    AiLevel,
    IdentityProvider,
    Package,
    PaymentProvider,
    PaymentStatus,
    RenewalStatus,
    UserRole,
)
from app.models.membership import Membership
from app.models.payment import PaymentRecord
from app.models.user import User, UserIdentity


async def test_create_user_identity_membership_payment(db_session: AsyncSession) -> None:
    email = f"test_{uuid.uuid4().hex}@example.com"

    user = User(display_name="Test User")
    user.identities.append(
        UserIdentity(
            provider=IdentityProvider.email,
            identifier=email,
            password_hash="not-a-real-hash",
            is_primary=True,
        )
    )
    user.membership = Membership(
        package=Package.entry_49,
        access_state=AccessState.active,
        ai_level=AiLevel.basic_chat,
        renewal_status=RenewalStatus.manual,
    )
    user.payments.append(
        PaymentRecord(
            provider=PaymentProvider.crypto,
            package=Package.entry_49,
            status=PaymentStatus.succeeded,
            amount=Decimal("49.00"),
            currency="USDT",
            tx_hash="0xabc123",
            chain="bsc",
        )
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    user_id = user.id
    assert user.role is UserRole.customer  # column default applied

    # Identity is scoped to the user and unique-normalized.
    identities = (
        (await db_session.execute(select(UserIdentity).where(UserIdentity.user_id == user_id)))
        .scalars()
        .all()
    )
    assert len(identities) == 1
    assert identities[0].identifier == email
    assert identities[0].provider is IdentityProvider.email

    # Exactly one membership per user, with the expected package/level.
    membership = (
        await db_session.execute(select(Membership).where(Membership.user_id == user_id))
    ).scalar_one()
    assert membership.package is Package.entry_49
    assert membership.ai_level is AiLevel.basic_chat
    assert membership.access_state is AccessState.active

    # Payment recorded and scoped to the user.
    payment = (
        await db_session.execute(select(PaymentRecord).where(PaymentRecord.user_id == user_id))
    ).scalar_one()
    assert payment.amount == Decimal("49.00")
    assert payment.provider is PaymentProvider.crypto
    assert payment.status is PaymentStatus.succeeded
