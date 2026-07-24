"""Admin routes. Every endpoint here requires an admin role.

This is the server-side gate for the Founder/Admin backend; the concrete
management endpoints (knowledge, rules, prompts, ...) are added in later weeks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/overview")
async def overview(admin: User = Depends(require_admin)) -> dict[str, str]:
    return {
        "admin_id": str(admin.id),
        "display_name": admin.display_name or "",
        "role": admin.role.value,
    }
