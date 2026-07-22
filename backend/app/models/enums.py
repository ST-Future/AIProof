"""Shared enum values used across models and schemas.

All enums are stored as strings (``native_enum=False`` on the columns) so the
value and the name are identical — keeps migrations simple and lets us add
values later without Postgres ENUM type surgery.
"""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    customer = "customer"
    admin = "admin"


class AccountStatus(StrEnum):
    active = "active"
    suspended = "suspended"


class IdentityProvider(StrEnum):
    email = "email"
    wallet = "wallet"


class Package(StrEnum):
    none = "none"
    entry_49 = "entry_49"  # $49 Entry package
    coaching_199 = "coaching_199"  # $199 Monthly AI Coaching


class AccessState(StrEnum):
    inactive = "inactive"
    active = "active"
    expired = "expired"
    paused = "paused"


class AiLevel(StrEnum):
    none = "none"
    basic_chat = "basic_chat"  # $49 Basic AI Chat
    energy_guide = "energy_guide"  # $199 Energy Field AI Guide


class RenewalStatus(StrEnum):
    none = "none"
    auto = "auto"  # Stripe / PayPal recurring subscription
    manual = "manual"  # crypto 30-day unlock, renewed by paying again


class PaymentProvider(StrEnum):
    stripe = "stripe"
    paypal = "paypal"
    crypto = "crypto"


class PaymentStatus(StrEnum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"
