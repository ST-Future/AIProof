"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings


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
