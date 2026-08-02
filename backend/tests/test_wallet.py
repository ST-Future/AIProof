"""Wallet auth: nonce → sign → verify login, same-wallet reuse, linking, bad sig."""

from __future__ import annotations

import uuid

from eth_account import Account
from eth_account.messages import encode_defunct
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import IdentityProvider
from app.models.user import User, UserIdentity
from tests.conftest import TEST_EMAIL_DOMAIN


async def _sign_in_message(client: AsyncClient, acct: Account) -> tuple[str, str]:
    """Get a nonce, sign it, and return (signature, nonce_token)."""
    nonce = await client.post("/api/auth/wallet/nonce", json={"address": acct.address})
    body = nonce.json()
    signed = Account.sign_message(encode_defunct(text=body["message"]), private_key=acct.key)
    return signed.signature.hex(), body["nonce_token"]


async def test_wallet_login_creates_and_reuses_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    acct = Account.create()
    address = acct.address.lower()
    try:
        sig, token = await _sign_in_message(client, acct)
        first = await client.post(
            "/api/auth/wallet/verify",
            json={"address": acct.address, "signature": sig, "nonce_token": token},
        )
        assert first.status_code == 200
        access = first.json()["access_token"]
        user_id = first.json()["user"]["id"]

        # A wallet identity now exists for this address.
        me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
        assert me.status_code == 200 and me.json()["id"] == user_id

        # Signing in again with the same wallet returns the same user.
        sig2, token2 = await _sign_in_message(client, acct)
        second = await client.post(
            "/api/auth/wallet/verify",
            json={"address": acct.address, "signature": sig2, "nonce_token": token2},
        )
        assert second.json()["user"]["id"] == user_id
    finally:
        ident = (
            await db_session.execute(select(UserIdentity).where(UserIdentity.identifier == address))
        ).scalar_one_or_none()
        if ident:
            await db_session.execute(delete(User).where(User.id == ident.user_id))
            await db_session.commit()


async def test_bad_signature_rejected(client: AsyncClient) -> None:
    acct = Account.create()
    _, token = await _sign_in_message(client, acct)
    # Sign a *different* wallet's message but claim this address.
    other = Account.create()
    bad = Account.sign_message(encode_defunct(text="wrong message"), private_key=other.key)
    resp = await client.post(
        "/api/auth/wallet/verify",
        json={"address": acct.address, "signature": bad.signature.hex(), "nonce_token": token},
    )
    assert resp.status_code == 401


async def test_link_wallet_to_email_user(client: AsyncClient, db_session: AsyncSession) -> None:
    signup = await client.post(
        "/api/auth/signup",
        json={"email": f"user_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}", "password": "password12"},
    )
    auth = {"Authorization": f"Bearer {signup.json()['access_token']}"}
    user_id = signup.json()["user"]["id"]
    acct = Account.create()
    try:
        sig, token = await _sign_in_message(client, acct)
        linked = await client.post(
            "/api/auth/wallet/link",
            headers=auth,
            json={"address": acct.address, "signature": sig, "nonce_token": token},
        )
        assert linked.status_code == 200

        # The email user now owns both an email and a wallet identity.
        idents = (
            (
                await db_session.execute(
                    select(UserIdentity).where(UserIdentity.user_id == uuid.UUID(user_id))
                )
            )
            .scalars()
            .all()
        )
        providers = {i.provider for i in idents}
        assert IdentityProvider.email in providers
        assert IdentityProvider.wallet in providers
    finally:
        await db_session.execute(delete(User).where(User.id == uuid.UUID(user_id)))
        await db_session.commit()
