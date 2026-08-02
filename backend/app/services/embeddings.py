"""RAG embedding pipeline for published knowledge.

The embedder sits behind a small provider abstraction so OpenAI can be swapped
in later (Week 4) without changing the pipeline. A deterministic, dependency-free
embedder is the default, so embedding + vector search work offline and in tests.

Retrieval only ever returns chunks of **published** knowledge the user's AI level
can access.
"""

from __future__ import annotations

import hashlib
import math
import re
import uuid
from typing import Any, Protocol

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.enums import AiLevel, KnowledgeStatus
from app.models.knowledge import EMBEDDING_DIM, KnowledgeEmbedding, KnowledgeEntry

_TOKEN = re.compile(r"[a-z0-9]+")
_LEVEL_RANK: dict[AiLevel, int] = {
    AiLevel.none: 0,
    AiLevel.basic_chat: 1,
    AiLevel.energy_guide: 2,
}


# --------------------------------- embedder --------------------------------


class Embedder(Protocol):
    name: str

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class DeterministicEmbedder:
    """Hashed bag-of-words vectors, L2-normalized. Reproducible, no network.

    Similar text (shared tokens) yields high cosine similarity, which is enough
    for keyword-relevant retrieval in dev/tests.
    """

    name = "deterministic-hash-v1"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    @staticmethod
    def _one(text: str) -> list[float]:
        vec = [0.0] * EMBEDDING_DIM
        for tok in _TOKEN.findall(text.lower()):
            idx = int(hashlib.md5(tok.encode()).hexdigest(), 16) % EMBEDDING_DIM
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm:
            vec = [v / norm for v in vec]
        return vec


class OpenAIEmbedder:
    """OpenAI embeddings (wired for Week 4). Requires the ``openai`` package + key."""

    name = "openai:text-embedding-3-small"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        from openai import AsyncOpenAI  # lazy import; optional dependency

        client = AsyncOpenAI(api_key=get_settings().openai_api_key)
        resp = await client.embeddings.create(model="text-embedding-3-small", input=texts)
        return [item.embedding for item in resp.data]


def get_embedder() -> Embedder:
    settings = get_settings()
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbedder()
    return DeterministicEmbedder()


# --------------------------------- chunking --------------------------------


def chunk_text(text: str, *, max_chars: int = 800) -> list[str]:
    """Split content into paragraph-ish chunks, further splitting long ones."""
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    for para in (p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()):
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            for i in range(0, len(para), max_chars):
                chunks.append(para[i : i + max_chars])
    return chunks or [text]


# --------------------------------- pipeline --------------------------------


async def embed_knowledge_entry(db: AsyncSession, entry: KnowledgeEntry) -> int:
    """(Re)generate embeddings for an entry: replace any existing chunks."""
    await db.execute(delete(KnowledgeEmbedding).where(KnowledgeEmbedding.knowledge_id == entry.id))
    chunks = chunk_text(entry.body)
    if not chunks:
        return 0
    embedder = get_embedder()
    vectors = await embedder.embed(chunks)
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        db.add(
            KnowledgeEmbedding(
                knowledge_id=entry.id,
                chunk_index=index,
                content=chunk,
                embedding=vector,
                model=embedder.name,
            )
        )
    await db.flush()
    return len(chunks)


async def delete_entry_embeddings(db: AsyncSession, knowledge_id: uuid.UUID) -> None:
    await db.execute(
        delete(KnowledgeEmbedding).where(KnowledgeEmbedding.knowledge_id == knowledge_id)
    )
    await db.flush()


async def search(
    db: AsyncSession,
    query: str,
    *,
    max_ai_level: AiLevel = AiLevel.energy_guide,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return the most relevant published chunks the given AI level can access."""
    embedder = get_embedder()
    query_vec = (await embedder.embed([query]))[0]

    allowed = [lvl for lvl, rank in _LEVEL_RANK.items() if rank <= _LEVEL_RANK[max_ai_level]]
    distance = KnowledgeEmbedding.embedding.cosine_distance(query_vec)
    stmt = (
        select(KnowledgeEmbedding, KnowledgeEntry, distance.label("distance"))
        .join(KnowledgeEntry, KnowledgeEmbedding.knowledge_id == KnowledgeEntry.id)
        .where(
            KnowledgeEntry.status == KnowledgeStatus.published,
            KnowledgeEntry.min_ai_level.in_(allowed),
        )
        .order_by(distance)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "knowledge_id": str(entry.id),
            "title": entry.title,
            "chunk_index": emb.chunk_index,
            "content": emb.content,
            "distance": float(dist),
        }
        for emb, entry, dist in rows
    ]
