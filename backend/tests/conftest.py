"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.db import get_db
from app.main import app
from app.models.user import User, UserIdentity

# Tests create identities under this domain so cleanup is a single delete.
# (Use a real-looking domain; email-validator rejects reserved TLDs like .local.)
TEST_EMAIL_DOMAIN = "authtest.example.com"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """A per-test async session on a NullPool engine.

    A dedicated engine per test (disposed at teardown) avoids asyncpg
    connections outliving pytest-asyncio's event loop.
    """
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            yield session
            await session.rollback()
    finally:
        await engine.dispose()


async def _cleanup_test_users(maker: async_sessionmaker[AsyncSession]) -> None:
    async with maker() as session:
        subq = select(UserIdentity.user_id).where(
            UserIdentity.identifier.like(f"%@{TEST_EMAIL_DOMAIN}")
        )
        await session.execute(delete(User).where(User.id.in_(subq)))
        await session.commit()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client bound to the app, with ``get_db`` backed by a NullPool engine.

    Endpoints commit real rows; test users (``*@authtest.local``) are deleted on
    teardown so the dev DB stays clean.
    """
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            yield http_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        await _cleanup_test_users(maker)
        await engine.dispose()
