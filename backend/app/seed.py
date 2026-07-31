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
from app.models.enums import (
    Package,
    PromptStatus,
    RiskSeverity,
    RuleStatus,
    SalesTriggerMode,
)
from app.models.rules import AgentRule, BlockedClaim, PromptVersion, RiskRule, SalesTrigger
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
    ("general", ["unusual symptoms", "numbness", "severe pain"], RiskSeverity.medium),
]

# Medical-claim terms the Agent must never use.
BLOCKED_CLAIMS: list[str] = [
    "cure",
    "heal",
    "treat disease",
    "diagnose",
    "guaranteed weight loss",
    "guaranteed healing",
    "life extension",
    "medical treatment",
    "reverse illness",
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


# (name, priority, is_safety_override, status, conditions, actions) — the plan's examples.
AGENT_RULES: list[tuple[str, int, bool, dict[str, object], dict[str, object]]] = [
    (
        "Safety overrides sales on discomfort",
        1,
        True,
        {"intents": ["discomfort"], "risks": ["cardiac", "respiratory", "neurological", "anxiety"]},
        {
            "type": "safety_first",
            "disable_sales": True,
            "message_hint": "Slow or stop the practice; suggest professional support if serious.",
        },
    ),
    (
        "Encourage patient beginners",
        50,
        False,
        {
            "stages": ["basic_training"],
            "intents": ["no_sensation", "training_feedback"],
            "max_completed_sessions": 3,
        },
        {
            "type": "continue_basics",
            "lower_difficulty": True,
            "disable_sales": True,
            "message_hint": "Encourage patience, check completion, suggest a small adjustment.",
        },
    ),
    (
        "Cooldown after purchase refusal",
        40,
        False,
        {"intents": ["refuse_purchase"]},
        {"type": "start_cooldown", "disable_sales": True, "cooldown_seconds": 86400},
    ),
    (
        "Answer price and package questions",
        60,
        False,
        {"intents": ["price_question", "product_inquiry"]},
        {
            "type": "allow_sales",
            "allow_sales": True,
            "message_hint": "Explain the $49 and $199 options clearly.",
        },
    ),
    (
        "Soft upgrade for stable 7-day users",
        70,
        False,
        {"min_day_count": 7, "intents": ["upgrade_interest"]},
        {
            "type": "allow_sales",
            "allow_sales": True,
            "message_hint": "Introduce the next stage or $199 guide softly.",
        },
    ),
]


# (name, mode, priority, target_package, conditions, cooldown_seconds)
SALES_TRIGGERS: list[
    tuple[str, SalesTriggerMode, int, Package | None, dict[str, object], int | None]
] = [
    (
        "Block sales during discomfort",
        SalesTriggerMode.block,
        1,
        None,
        {"intents": ["discomfort"], "risks": ["cardiac", "respiratory", "neurological", "anxiety"]},
        None,
    ),
    (
        "Block sales during refusal cooldown",
        SalesTriggerMode.block,
        5,
        None,
        {"intents": ["refuse_purchase"]},
        86400,
    ),
    (
        "Allow price and package explanations",
        SalesTriggerMode.allow,
        60,
        None,
        {"intents": ["price_question", "product_inquiry"]},
        None,
    ),
    (
        "Allow upgrade for stable 7-day users",
        SalesTriggerMode.allow,
        70,
        Package.coaching_199,
        {"min_day_count": 7, "intents": ["upgrade_interest"]},
        None,
    ),
]


async def seed_sales_triggers(session: AsyncSession) -> int:
    existing = set((await session.execute(select(SalesTrigger.name))).scalars().all())
    created = 0
    for name, mode, priority, target, conditions, cooldown in SALES_TRIGGERS:
        if name in existing:
            continue
        session.add(
            SalesTrigger(
                name=name,
                conditions=conditions,
                target_package=target,
                mode=mode,
                priority=priority,
                status=RuleStatus.active,
                cooldown_seconds=cooldown,
            )
        )
        created += 1
    return created


async def seed_blocked_claims(session: AsyncSession) -> int:
    existing = set((await session.execute(select(BlockedClaim.term))).scalars().all())
    created = 0
    for term in BLOCKED_CLAIMS:
        if term in existing:
            continue
        session.add(BlockedClaim(term=term, is_active=True))
        created += 1
    return created


async def seed_agent_rules(session: AsyncSession) -> int:
    existing = set((await session.execute(select(AgentRule.name))).scalars().all())
    created = 0
    for name, priority, safety, conditions, actions in AGENT_RULES:
        if name in existing:
            continue
        session.add(
            AgentRule(
                name=name,
                conditions=conditions,
                actions=actions,
                priority=priority,
                status=RuleStatus.active,
                is_safety_override=safety,
                cooldown_seconds=actions.get("cooldown_seconds"),
            )
        )
        created += 1
    return created


async def main() -> None:
    async with SessionLocal() as session:
        stages = await seed_stages(session)
        risks = await seed_risk_rules(session)
        prompts = await seed_default_prompt(session)
        rules = await seed_agent_rules(session)
        triggers = await seed_sales_triggers(session)
        claims = await seed_blocked_claims(session)
        await session.commit()
    await engine.dispose()
    print(
        f"Seed complete: +{stages} stages, +{risks} risk rules, "
        f"+{prompts} prompt versions, +{rules} agent rules, "
        f"+{triggers} sales triggers, +{claims} blocked claims"
    )


if __name__ == "__main__":
    asyncio.run(main())
