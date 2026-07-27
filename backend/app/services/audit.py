"""Admin audit trail helper."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AdminAction


async def record_admin_action(
    db: AsyncSession,
    *,
    admin_id: uuid.UUID | None,
    action: str,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    detail: dict[str, Any] | None = None,
) -> AdminAction:
    """Add an ``admin_actions`` row to the session (caller commits)."""
    record = AdminAction(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
    )
    db.add(record)
    return record
