"""Decision-layer models: agent rules, sales triggers, risk rules, prompts.

Conditions and actions are stored as structured JSON (documented shape), not
free text, so the rules engine can evaluate them deterministically.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.enums import Package, PromptStatus, RiskSeverity, RuleStatus, SalesTriggerMode


class AgentRule(TimestampMixin, Base):
    __tablename__ = "agent_rules"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    actions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    status: Mapped[RuleStatus] = mapped_column(
        SAEnum(RuleStatus, native_enum=False, length=20),
        default=RuleStatus.draft,
        nullable=False,
    )
    cooldown_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_safety_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SalesTrigger(TimestampMixin, Base):
    __tablename__ = "sales_triggers"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    target_package: Mapped[Package | None] = mapped_column(
        SAEnum(Package, native_enum=False, length=20), nullable=True
    )
    mode: Mapped[SalesTriggerMode] = mapped_column(
        SAEnum(SalesTriggerMode, native_enum=False, length=20),
        default=SalesTriggerMode.allow,
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    status: Mapped[RuleStatus] = mapped_column(
        SAEnum(RuleStatus, native_enum=False, length=20),
        default=RuleStatus.draft,
        nullable=False,
    )
    cooldown_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RiskRule(TimestampMixin, Base):
    __tablename__ = "risk_rules"

    id: Mapped[uuid.UUID] = uuid_pk()
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    severity: Mapped[RiskSeverity] = mapped_column(
        SAEnum(RiskSeverity, native_enum=False, length=20),
        default=RiskSeverity.medium,
        nullable=False,
    )
    # Safe fallback response / action reference used when this risk fires.
    fallback_action: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromptVersion(TimestampMixin, Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("key", "version", name="uq_prompt_key_version"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    # Grouping key (e.g. "system.base" or a stage/level-specific key).
    key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PromptStatus] = mapped_column(
        SAEnum(PromptStatus, native_enum=False, length=20),
        default=PromptStatus.draft,
        nullable=False,
    )
    # The currently published version for this key.
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
