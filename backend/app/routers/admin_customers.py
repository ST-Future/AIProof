"""Admin customer directory route."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.user import User
from app.schemas.profile import CustomerSummary
from app.services import customers as svc

router = APIRouter(prefix="/api/admin/customers", tags=["admin:customers"])


@router.get("", response_model=list[CustomerSummary])
async def list_customers(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[CustomerSummary]:
    return await svc.list_customers(db)
