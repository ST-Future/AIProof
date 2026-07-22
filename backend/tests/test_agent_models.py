"""Integration test for the agent/knowledge/conversation schema.

Exercises the Week 1 Wednesday tables (knowledge + embedding with pgvector,
conversation + message, agent run) through the async ORM layer. Rolls back.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import AgentRun, Conversation, Message
from app.models.enums import KnowledgeStatus, MessageRole, RunStatus
from app.models.knowledge import EMBEDDING_DIM, KnowledgeEmbedding, KnowledgeEntry
from app.models.user import User


async def test_knowledge_embedding_and_conversation_flow(db_session: AsyncSession) -> None:
    # Knowledge entry with a pgvector embedding chunk.
    entry = KnowledgeEntry(
        title="Box breathing basics",
        body="Inhale 4, hold 4, exhale 4, hold 4.",
        category="breathing",
        status=KnowledgeStatus.published,
        tags=["breathing", "beginner"],
    )
    entry.embeddings.append(
        KnowledgeEmbedding(
            chunk_index=0,
            content="Inhale 4, hold 4, exhale 4, hold 4.",
            embedding=[0.01] * EMBEDDING_DIM,
            model="text-embedding-3-small",
        )
    )
    db_session.add(entry)

    # A user with a conversation, one message, and a logged agent run.
    user = User(display_name="Runner")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id, title="First chat")
    conversation.messages.append(Message(role=MessageRole.user, content="I feel nothing yet."))
    db_session.add(conversation)

    run = AgentRun(
        user_id=user.id,
        user_message="I feel nothing yet.",
        intent="training_feedback",
        rule_ids=[str(uuid.uuid4())],
        knowledge_ids=[str(entry.id)],
        status=RunStatus.success,
        total_tokens=42,
        latency_ms=123,
    )
    db_session.add(run)
    await db_session.flush()

    # Embedding round-trips at the right dimensionality and is linked to the entry.
    embeddings = (
        (
            await db_session.execute(
                select(KnowledgeEmbedding).where(KnowledgeEmbedding.knowledge_id == entry.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(embeddings) == 1
    assert len(embeddings[0].embedding) == EMBEDDING_DIM

    # Conversation, message, and run are scoped to the user.
    messages = (
        (
            await db_session.execute(
                select(Message).where(Message.conversation_id == conversation.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(messages) == 1
    assert messages[0].role is MessageRole.user

    fetched_run = (
        await db_session.execute(select(AgentRun).where(AgentRun.user_id == user.id))
    ).scalar_one()
    assert fetched_run.intent == "training_feedback"
    assert fetched_run.knowledge_ids == [str(entry.id)]
    assert fetched_run.status is RunStatus.success
