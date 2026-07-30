"""Energy Profile generation and initial training-state setup.

The Energy Profile is a deterministic, rule-based mapping from the assessment
answers (no model call in Phase 1). Both the profile and the training state are
upserted, so re-submitting the assessment never duplicates rows or resets a
customer's existing progress.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import EnergyProfile
from app.models.training import TrainingStage, UserTrainingState

_LEVEL = {"beginner": "beginner", "some": "intermediate", "experienced": "advanced"}
_LEVEL_WORD = {
    "beginner": "new to practice",
    "some": "somewhat experienced",
    "experienced": "experienced",
}


def _intensity(stress: str, energy: str, experience: str) -> str:
    if stress == "high" or energy == "low":
        return "gentle"
    if energy == "high" and experience != "beginner":
        return "moderate"
    return "balanced"


def generate_energy_profile(answers: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return a (summary, traits) pair derived from assessment answers."""
    experience = str(answers.get("experience", "beginner"))
    stress = str(answers.get("stress_level", "moderate"))
    energy = str(answers.get("energy_level", "moderate"))
    sleep = str(answers.get("sleep_quality", "fair"))
    goals = list(answers.get("goals", []))
    minutes = int(answers.get("minutes_per_day", 10))

    intensity = _intensity(stress, energy, experience)
    traits: dict[str, Any] = {
        "level": _LEVEL.get(experience, "beginner"),
        "intensity": intensity,
        "focus_areas": goals,
        "recommended_minutes": minutes,
        "stress_level": stress,
        "energy_level": energy,
        "sleep_quality": sleep,
    }

    goal_words = ", ".join(g.replace("_", " ") for g in goals)
    summary = (
        f"You're {_LEVEL_WORD.get(experience, 'new to practice')}. "
        f"Right now your stress feels {stress}, your energy is {energy}, and your sleep is "
        f"{sleep}. We'll begin with {intensity} practices of about {minutes} minutes a day"
        + (f", focused on {goal_words}." if goal_words else ".")
    )
    return summary, traits


def starting_stage_key(answers: dict[str, Any]) -> str:
    """Experienced customers can start a step further along."""
    return "basic_training" if answers.get("experience") == "experienced" else "beginner"


async def upsert_energy_profile(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    source_assessment_id: uuid.UUID | None,
    summary: str,
    traits: dict[str, Any],
) -> EnergyProfile:
    profile = (
        await db.execute(select(EnergyProfile).where(EnergyProfile.user_id == user_id))
    ).scalar_one_or_none()
    if profile is not None:
        profile.summary = summary
        profile.traits = traits
        profile.source_assessment_id = source_assessment_id
    else:
        profile = EnergyProfile(
            user_id=user_id,
            summary=summary,
            traits=traits,
            source_assessment_id=source_assessment_id,
        )
        db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


async def initialize_training_state(
    db: AsyncSession, user_id: uuid.UUID, *, stage_key: str
) -> UserTrainingState:
    """Create the user's training state if missing (idempotent — never resets progress)."""
    stage = (
        await db.execute(select(TrainingStage).where(TrainingStage.key == stage_key))
    ).scalar_one_or_none()

    state = (
        await db.execute(select(UserTrainingState).where(UserTrainingState.user_id == user_id))
    ).scalar_one_or_none()

    if state is None:
        state = UserTrainingState(
            user_id=user_id,
            current_stage_id=stage.id if stage else None,
            day_count=0,
            completed_sessions=0,
            interruption_days=0,
        )
        db.add(state)
    elif state.current_stage_id is None and stage is not None:
        # Fill in a stage if it was never set, but keep any existing progress.
        state.current_stage_id = stage.id

    await db.flush()
    await db.refresh(state)
    return state
