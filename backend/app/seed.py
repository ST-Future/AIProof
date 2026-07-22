"""Seed reference data (idempotent).

Seeds the admin-defined journey stages, a default published system prompt, and
the initial safety risk rules from the plan. Safe to run repeatedly — existing
rows (matched by natural key) are left untouched.

Run with:  python -m app.seed
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models.enums import PromptStatus, RiskSeverity
from app.models.rules import PromptVersion, RiskRule
from app.models.training import TrainingStage

# (key, display name, order) — the Phase 1 journey stages.
STAGES: list[tuple[str, str, int]] = [
    ("unassessed", "Unassessed", 0),
    ("beginner", "Beginner", 1),
    ("basic_training", "Basic Training", 2),
    ("adaptation", "Adaptation", 3),
    ("advanced_training", "Advanced Training", 4),
    ("paused", "Paused", 5),
    ("renewal_reminder", "Renewal Reminder", 6),
    ("completed", "Completed", 7),
]

# (category, keywords, severity) — safety-first detection seeds.
RISK_RULES: list[tuple[str, list[str], RiskSeverity]] = [
    ("cardiac", ["chest pain", "chest tightness", "heart pain"], RiskSeverity.high),
    (
        "respiratory",
        ["can't breathe", "breathing difficulty", "shortness of breath"],
        RiskSeverity.high,
    ),
    ("neurological", ["dizzy", "dizziness", "faint", "fainting"], RiskSeverity.medium),
    ("anxiety", ["panic attack", "severe anxiety", "anxiety attack"], RiskSeverity.medium),
]

DEFAULT_PROMPT_KEY = "system.base"
DEFAULT_PROMPT_CONTENT = (
    "You are the Great Energy Field guide. Stay within wellness, breathing, "
    "meditation, energy-practice, journaling, and personal-growth boundaries. "
    "Do not give medical diagnosis or treatment, and never promise healing, "
    "weight loss, or cures. Follow the decision rules provided to you: respect "
    "the user's training stage, apply safety handling first, and never push an "
    "upgrade during discomfort, anxiety, complaints, or a sales cooldown."
)


async def seed_stages(session: AsyncSession) -> int:
    existing = set((await session.execute(select(TrainingStage.key))).scalars().all())
    created = 0
    for key, name, order in STAGES:
        if key in existing:
            continue
        session.add(TrainingStage(key=key, name=name, order_index=order, is_active=True))
        created += 1
    return created


async def seed_risk_rules(session: AsyncSession) -> int:
    existing = set((await session.execute(select(RiskRule.category))).scalars().all())
    created = 0
    for category, keywords, severity in RISK_RULES:
        if category in existing:
            continue
        session.add(
            RiskRule(
                category=category,
                keywords=keywords,
                severity=severity,
                fallback_action={
                    "type": "safety_first",
                    "message": (
                        "Please pause your practice. If this feels serious, stop and "
                        "seek professional support."
                    ),
                    "disable_sales": True,
                },
                is_active=True,
            )
        )
        created += 1
    return created


async def seed_default_prompt(session: AsyncSession) -> int:
    exists = (
        await session.execute(
            select(PromptVersion.id).where(PromptVersion.key == DEFAULT_PROMPT_KEY)
        )
    ).first()
    if exists:
        return 0
    session.add(
        PromptVersion(
            key=DEFAULT_PROMPT_KEY,
            version=1,
            content=DEFAULT_PROMPT_CONTENT,
            status=PromptStatus.published,
            is_active=True,
        )
    )
    return 1


async def main() -> None:
    async with SessionLocal() as session:
        stages = await seed_stages(session)
        risks = await seed_risk_rules(session)
        prompts = await seed_default_prompt(session)
        await session.commit()
    await engine.dispose()
    print(f"Seed complete: +{stages} stages, +{risks} risk rules, +{prompts} prompt versions")


if __name__ == "__main__":
    asyncio.run(main())
