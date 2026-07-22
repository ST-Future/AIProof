"""Training domain models: stages, modules, sessions, and per-user state.

Training progress is driven by database state here (not guessed from chat
history), which is a Phase 1 acceptance requirement.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import AiLevel, SessionStatus


class TrainingStage(TimestampMixin, Base):
    __tablename__ = "training_stages"

    id: Mapped[uuid.UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Structured progression conditions to enter/advance this stage.
    entry_conditions: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TrainingModule(TimestampMixin, Base):
    __tablename__ = "training_modules"

    id: Mapped[uuid.UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_user: Mapped[str | None] = mapped_column(String(160), nullable=True)
    stage_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("training_stages.id", ondelete="SET NULL"), nullable=True
    )
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stop_conditions: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    next_module_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("training_modules.id", ondelete="SET NULL"), nullable=True
    )
    next_stage_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("training_stages.id", ondelete="SET NULL"), nullable=True
    )
    # Minimum AI level required to access this module.
    min_ai_level: Mapped[AiLevel] = mapped_column(
        SAEnum(AiLevel, native_enum=False, length=20), default=AiLevel.none, nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TrainingSession(TimestampMixin, Base):
    __tablename__ = "training_sessions"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    module_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("training_modules.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(SessionStatus, native_enum=False, length=20),
        default=SessionStatus.started,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)


class UserTrainingState(TimestampMixin, Base):
    __tablename__ = "user_training_state"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    current_stage_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("training_stages.id", ondelete="SET NULL"), nullable=True
    )
    current_module_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("training_modules.id", ondelete="SET NULL"), nullable=True
    )
    day_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_training_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    interruption_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Sales cooldown + flags (e.g. last upsell, refusal) kept structured.
    sales_cooldown_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sales_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
