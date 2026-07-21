"""ORM models package.

Concrete tables (users, memberships, knowledge_entries, ...) are added in
Week 1 Tuesday/Wednesday. Importing this package makes all models visible to
Alembic's autogenerate via ``app.db.Base.metadata``.
"""

from app.db import Base  # noqa: F401  (re-exported for Alembic target_metadata)
