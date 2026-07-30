"""Admin customer directory: assemble each customer's resolved state."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import BackgroundAssessment, EnergyProfile
from app.models.enums import AccessState, IdentityProvider, Package, UserRole
from app.models.membership import Membership
from app.models.training import TrainingStage, UserTrainingState
from app.models.user import User, UserIdentity
from app.schemas.profile import CustomerSummary


async def list_customers(db: AsyncSession) -> list[CustomerSummary]:
    users = (
        (
            await db.execute(
                select(User).where(User.role == UserRole.customer).order_by(User.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    if not users:
        return []
    ids = [u.id for u in users]

    emails: dict[str, str] = {}
    for ident in (
        await db.execute(
            select(UserIdentity).where(
                UserIdentity.user_id.in_(ids),
                UserIdentity.provider == IdentityProvider.email,
            )
        )
    ).scalars():
        emails.setdefault(str(ident.user_id), ident.identifier)

    memberships = {
        m.user_id: m
        for m in (await db.execute(select(Membership).where(Membership.user_id.in_(ids)))).scalars()
    }
    profiles = {
        p.user_id: p
        for p in (
            await db.execute(select(EnergyProfile).where(EnergyProfile.user_id.in_(ids)))
        ).scalars()
    }
    states = {
        s.user_id: s
        for s in (
            await db.execute(select(UserTrainingState).where(UserTrainingState.user_id.in_(ids)))
        ).scalars()
    }
    assessed = {
        row[0]
        for row in (
            await db.execute(
                select(BackgroundAssessment.user_id).where(BackgroundAssessment.user_id.in_(ids))
            )
        ).all()
    }
    stage_names = {s.id: s.name for s in (await db.execute(select(TrainingStage))).scalars()}

    result: list[CustomerSummary] = []
    for u in users:
        m = memberships.get(u.id)
        p = profiles.get(u.id)
        st = states.get(u.id)
        stage = stage_names.get(st.current_stage_id) if st and st.current_stage_id else None
        result.append(
            CustomerSummary(
                id=u.id,
                email=emails.get(str(u.id)),
                display_name=u.display_name,
                created_at=u.created_at,
                package=m.package if m else Package.none,
                access_state=m.access_state if m else AccessState.inactive,
                has_assessment=u.id in assessed,
                energy_summary=p.summary if p else None,
                stage=stage,
                day_count=st.day_count if st else None,
                completed_sessions=st.completed_sessions if st else None,
            )
        )
    return result
