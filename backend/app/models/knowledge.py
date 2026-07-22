"""Knowledge base + RAG embedding models."""

from __future__ import annotations

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import AiLevel, KnowledgeStatus

# OpenAI text-embedding-3-small dimensionality (Phase 1 default provider).
EMBEDDING_DIM = 1536


class KnowledgeEntry(TimestampMixin, Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    status: Mapped[KnowledgeStatus] = mapped_column(
        SAEnum(KnowledgeStatus, native_enum=False, length=20),
        default=KnowledgeStatus.draft,
        index=True,
        nullable=False,
    )
    # Minimum AI level required to surface this content to a customer.
    min_ai_level: Mapped[AiLevel] = mapped_column(
        SAEnum(AiLevel, native_enum=False, length=20), default=AiLevel.none, nullable=False
    )
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    safety_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    embeddings: Mapped[list[KnowledgeEmbedding]] = relationship(
        back_populates="entry", cascade="all, delete-orphan"
    )


class KnowledgeEmbedding(TimestampMixin, Base):
    __tablename__ = "knowledge_embeddings"

    id: Mapped[uuid.UUID] = uuid_pk()
    knowledge_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("knowledge_entries.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    entry: Mapped[KnowledgeEntry] = relationship(back_populates="embeddings")
