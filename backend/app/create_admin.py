"""Create or promote a founder/admin account.

Run with:
    python -m app.create_admin <email> <password> [display_name]

If the email already exists, the user is promoted to admin (and, if a password
is given, its password is reset). Otherwise a new admin account is created.
"""

from __future__ import annotations

import asyncio
import sys

from app.core.security import hash_password
from app.db import SessionLocal, engine
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.user import User, UserIdentity
from app.services.auth import _get_email_identity, _normalize_email


async def create_or_promote_admin(email: str, password: str, display_name: str | None) -> str:
    async with SessionLocal() as session:
        identity = await _get_email_identity(session, email)
        if identity is not None:
            user = await session.get(User, identity.user_id)
            assert user is not None
            user.role = UserRole.admin
            identity.password_hash = hash_password(password)
            if display_name:
                user.display_name = display_name
            action = "promoted"
        else:
            user = User(display_name=display_name, role=UserRole.admin)
            user.identities.append(
                UserIdentity(
                    provider=IdentityProvider.email,
                    identifier=_normalize_email(email),
                    password_hash=hash_password(password),
                    is_primary=True,
                    is_verified=True,
                )
            )
            user.membership = Membership()
            session.add(user)
            action = "created"
        await session.commit()
    await engine.dispose()
    return action


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: python -m app.create_admin <email> <password> [display_name]")
        raise SystemExit(1)
    email, password = sys.argv[1], sys.argv[2]
    display_name = sys.argv[3] if len(sys.argv) > 3 else None
    action = asyncio.run(create_or_promote_admin(email, password, display_name))
    print(f"Admin {action}: {email}")


if __name__ == "__main__":
    main()
