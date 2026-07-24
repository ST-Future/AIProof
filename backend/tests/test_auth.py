"""Auth flow tests: signup, login, /me, and admin protection."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.enums import IdentityProvider, UserRole
from app.models.membership import Membership
from app.models.user import User, UserIdentity
from tests.conftest import TEST_EMAIL_DOMAIN


def _email() -> str:
    return f"user_{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}"


async def test_signup_returns_token_and_me_works(client: AsyncClient) -> None:
    email = _email()
    resp = await client.post(
        "/api/auth/signup",
        json={"email": email, "password": "supersecret1", "display_name": "Ann"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "customer"
    token = body["access_token"]

    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == body["user"]["id"]


async def test_duplicate_signup_conflicts(client: AsyncClient) -> None:
    email = _email()
    payload = {"email": email, "password": "supersecret1"}
    assert (await client.post("/api/auth/signup", json=payload)).status_code == 201
    dup = await client.post("/api/auth/signup", json=payload)
    assert dup.status_code == 409


async def test_login_wrong_and_right_password(client: AsyncClient) -> None:
    email = _email()
    await client.post("/api/auth/signup", json={"email": email, "password": "rightpass1"})

    wrong = await client.post("/api/auth/login", json={"email": email, "password": "nope"})
    assert wrong.status_code == 401

    ok = await client.post("/api/auth/login", json={"email": email, "password": "rightpass1"})
    assert ok.status_code == 200
    assert ok.json()["access_token"]


async def test_admin_endpoint_requires_admin(client: AsyncClient, db_session: AsyncSession) -> None:
    # No token -> 401.
    assert (await client.get("/api/admin/overview")).status_code == 401

    # Customer token -> 403.
    signup = await client.post(
        "/api/auth/signup", json={"email": _email(), "password": "customerpass1"}
    )
    customer_token = signup.json()["access_token"]
    forbidden = await client.get(
        "/api/admin/overview", headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert forbidden.status_code == 403

    # Admin token -> 200.
    admin = User(display_name="Founder", role=UserRole.admin)
    admin.identities.append(
        UserIdentity(
            provider=IdentityProvider.email,
            identifier=_email(),
            password_hash="x",
            is_primary=True,
        )
    )
    admin.membership = Membership()
    db_session.add(admin)
    await db_session.commit()

    admin_token = create_access_token(subject=str(admin.id), role=UserRole.admin.value)
    ok = await client.get("/api/admin/overview", headers={"Authorization": f"Bearer {admin_token}"})
    assert ok.status_code == 200
    assert ok.json()["role"] == "admin"


async def test_invalid_token_rejected(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert resp.status_code == 401
