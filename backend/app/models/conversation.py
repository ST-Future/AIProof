"""Conversation, message, agent-run, and feedback models.

``agent_runs`` is the explainability log: every Agent call records the user
state, intent, risk, rule/knowledge ids, prompt version, tokens, latency,
output, and errors so the admin can see *why* the AI answered.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import AiLevel, FeedbackSource, MessageRole, RiskSeverity, RunStatus


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ai_level: Mapped[AiLevel] = mapped_column(
        SAEnum(AiLevel, native_enum=False, length=20), default=AiLevel.none, nullable=False
    )

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    user_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(60), nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    risk_severity: Mapped[RiskSeverity | None] = mapped_column(
        SAEnum(RiskSeverity, native_enum=False, length=20), nullable=True
    )
    rule_ids: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    knowledge_ids: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("prompt_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_state_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[RunStatus] = mapped_column(
        SAEnum(RunStatus, native_enum=False, length=20),
        default=RunStatus.success,
        nullable=False,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = uuid_pk()
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole, native_enum=False, length=20), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Links an assistant message back to the run that produced it.
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class AiFeedback(TimestampMixin, Base):
    __tablename__ = "ai_feedback"

    id: Mapped[uuid.UUID] = uuid_pk()
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Who gave the feedback (customer or admin).
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    source: Mapped[FeedbackSource] = mapped_column(
        SAEnum(FeedbackSource, native_enum=False, length=20),
        default=FeedbackSource.admin,
        nullable=False,
    )
    # e.g. too_general, inaccurate, too_strong, too_weak, unsafe, missing_sales.
    labels: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
