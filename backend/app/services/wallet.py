"""Wallet (Web3) auth: SIWE-style nonce challenge + signature verification.

Stateless nonce (signed token), signature recovered with ``eth_account``.
Supports wallet-only sign-in/sign-up and linking a wallet to an existing user.
"""

from __future__ import annotations

import secrets

import jwt
from eth_account import Account
from eth_account.messages import encode_defunct
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_wallet_nonce_token, decode_wallet_nonce_token
from app.models.enums import IdentityProvider
from app.models.membership import Membership
from app.models.user import User, UserIdentity


class WalletVerificationError(Exception):
    """Raised when a wallet signature or nonce fails verification."""


class WalletAlreadyLinkedError(Exception):
    """Raised when a wallet is already linked to a different account."""


def normalize_address(address: str) -> str:
    return address.strip().lower()


def build_login_message(address: str, nonce: str) -> str:
    return (
        "Great Energy Field — sign in with your wallet.\n\n"
        f"Address: {address}\n"
        f"Nonce: {nonce}"
    )


def issue_nonce(address: str) -> tuple[str, str]:
    """Return (message_to_sign, nonce_token) for a wallet address."""
    addr = normalize_address(address)
    nonce = secrets.token_hex(16)
    return build_login_message(addr, nonce), create_wallet_nonce_token(addr, nonce)


def verify_signature(address: str, signature: str, nonce_token: str) -> str:
    """Validate the nonce token + signature; return the normalized address."""
    addr = normalize_address(address)
    try:
        payload = decode_wallet_nonce_token(nonce_token)
    except jwt.PyJWTError as exc:
        raise WalletVerificationError("Invalid or expired nonce") from exc
    if payload.get("purpose") != "wallet_nonce" or payload.get("sub") != addr:
        raise WalletVerificationError("Nonce does not match address")

    message = build_login_message(addr, str(payload.get("nonce", "")))
    try:
        recovered = Account.recover_message(encode_defunct(text=message), signature=signature)
    except Exception as exc:  # noqa: BLE001 - any recovery failure is an auth failure
        raise WalletVerificationError("Bad signature") from exc
    if normalize_address(recovered) != addr:
        raise WalletVerificationError("Signature does not match address")
    return addr


async def _get_wallet_identity(db: AsyncSession, address: str) -> UserIdentity | None:
    result = await db.execute(
        select(UserIdentity).where(
            UserIdentity.provider == IdentityProvider.wallet,
            UserIdentity.identifier == normalize_address(address),
        )
    )
    return result.scalar_one_or_none()


async def login_or_create_wallet_user(db: AsyncSession, address: str) -> User:
    """Return the user for this wallet, creating a wallet-only account if new."""
    identity = await _get_wallet_identity(db, address)
    if identity is not None:
        user = await db.get(User, identity.user_id)
        assert user is not None
        return user

    user = User()
    user.identities.append(
        UserIdentity(
            provider=IdentityProvider.wallet,
            identifier=normalize_address(address),
            is_primary=True,
            is_verified=True,
        )
    )
    user.membership = Membership()
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def link_wallet_to_user(db: AsyncSession, user: User, address: str) -> None:
    """Attach a wallet to an existing account (email↔wallet linking)."""
    identity = await _get_wallet_identity(db, address)
    if identity is not None:
        if identity.user_id != user.id:
            raise WalletAlreadyLinkedError(address)
        return  # already linked to this user — no-op
    db.add(
        UserIdentity(
            user_id=user.id,
            provider=IdentityProvider.wallet,
            identifier=normalize_address(address),
            is_verified=True,
        )
    )
    await db.flush()
