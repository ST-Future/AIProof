"""ORM models package.

Importing this package registers every model on ``app.db.Base.metadata`` so
Alembic autogenerate (via ``target_metadata``) can see them.
"""

from app.db import Base
from app.models.membership import Membership
from app.models.payment import PaymentRecord
from app.models.user import User, UserIdentity

__all__ = ["Base", "User", "UserIdentity", "Membership", "PaymentRecord"]
