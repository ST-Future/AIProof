"""Pydantic schemas for users and identities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import AccountStatus, IdentityProvider, UserRole


class UserCreate(BaseModel):
    """Email signup payload (used from Week 1 Thursday auth)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class IdentityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: IdentityProvider
    identifier: str
    is_primary: bool
    is_verified: bool


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    status: AccountStatus
    display_name: str | None
    created_at: datetime
