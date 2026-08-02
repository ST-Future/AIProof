"""Backfill RAG embeddings for all currently-published knowledge entries.

Run with:  python -m app.backfill_embeddings
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db import SessionLocal, engine
from app.models.enums import KnowledgeStatus
from app.models.knowledge import KnowledgeEntry
from app.services.embeddings import embed_knowledge_entry


async def main() -> None:
    async with SessionLocal() as session:
        entries = (
            (
                await session.execute(
                    select(KnowledgeEntry).where(KnowledgeEntry.status == KnowledgeStatus.published)
                )
            )
            .scalars()
            .all()
        )
        total_chunks = 0
        for entry in entries:
            total_chunks += await embed_knowledge_entry(session, entry)
        await session.commit()
    await engine.dispose()
    print(f"Backfilled {total_chunks} chunks across {len(entries)} published entries")


if __name__ == "__main__":
    asyncio.run(main())
