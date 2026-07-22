"""ORM models package.

Importing this package registers every model on ``app.db.Base.metadata`` so
Alembic autogenerate (via ``target_metadata``) can see them.
"""

from app.db import Base
from app.models.admin import AdminAction
from app.models.assessment import BackgroundAssessment, EnergyProfile
from app.models.conversation import AgentRun, AiFeedback, Conversation, Message
from app.models.knowledge import KnowledgeEmbedding, KnowledgeEntry
from app.models.membership import Membership
from app.models.payment import PaymentRecord
from app.models.rules import AgentRule, PromptVersion, RiskRule, SalesTrigger
from app.models.training import (
    TrainingModule,
    TrainingSession,
    TrainingStage,
    UserTrainingState,
)
from app.models.user import User, UserIdentity

__all__ = [
    "Base",
    # identity & membership
    "User",
    "UserIdentity",
    "Membership",
    "PaymentRecord",
    # assessment
    "BackgroundAssessment",
    "EnergyProfile",
    # training
    "TrainingStage",
    "TrainingModule",
    "TrainingSession",
    "UserTrainingState",
    # knowledge / RAG
    "KnowledgeEntry",
    "KnowledgeEmbedding",
    # decision layer
    "AgentRule",
    "SalesTrigger",
    "RiskRule",
    "PromptVersion",
    # conversation / logging
    "Conversation",
    "Message",
    "AgentRun",
    "AiFeedback",
    # admin
    "AdminAction",
]
