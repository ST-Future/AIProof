"""Background assessment schemas.

Wellness-framed onboarding questions only — no medical questions or claims.
The answer options are constrained (Literal) so submissions are validated.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Experience = Literal["beginner", "some", "experienced"]
Level = Literal["low", "moderate", "high"]
SleepQuality = Literal["poor", "fair", "good"]
Goal = Literal[
    "more_energy",
    "better_sleep",
    "less_stress",
    "emotional_balance",
    "focus",
    "general_wellbeing",
]
MinutesPerDay = Literal[5, 10, 20]


class AssessmentAnswers(BaseModel):
    """The customer's answers to the onboarding assessment."""

    experience: Experience
    stress_level: Level
    sleep_quality: SleepQuality
    energy_level: Level
    goals: list[Goal] = Field(default_factory=list)
    minutes_per_day: MinutesPerDay
    notes: str | None = Field(default=None, max_length=1000)


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    answers: dict[str, Any]
    version: int
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
