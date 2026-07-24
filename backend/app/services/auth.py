"""Auth service: email signup and authentication against the DB layer."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.enums import IdentityProvider
from app.models.membership import Membership
from app.models.user import User, UserIdentity


class EmailAlreadyRegisteredError(Exception):
    """Raised when signing up an email that already has an identity."""


def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def _get_email_identity(db: AsyncSession, email: str) -> UserIdentity | None:
    result = await db.execute(
        select(UserIdentity).where(
            UserIdentity.provider == IdentityProvider.email,
            UserIdentity.identifier == _normalize_email(email),
        )
    )
    return result.scalar_one_or_none()


async def signup_email_user(
    db: AsyncSession, email: str, password: str, display_name: str | None = None
) -> User:
    if await _get_email_identity(db, email) is not None:
        raise EmailAlreadyRegisteredError

    user = User(display_name=display_name)
    user.identities.append(
        UserIdentity(
            provider=IdentityProvider.email,
            identifier=_normalize_email(email),
            password_hash=hash_password(password),
            is_primary=True,
            is_verified=False,
        )
    )
    # Start with an empty (inactive) membership so access checks always resolve.
    user.membership = Membership()
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_email_user(db: AsyncSession, email: str, password: str) -> User | None:
    identity = await _get_email_identity(db, email)
    if identity is None or identity.password_hash is None:
        return None
    if not verify_password(password, identity.password_hash):
        return None
    return await db.get(User, identity.user_id)
