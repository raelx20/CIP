import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ConversationState(str, enum.Enum):
    ACTIVE = "active"
    WAITING_FOR_CITIZEN = "waiting_for_citizen"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMED_OUT = "timed_out"


class MessageRole(str, enum.Enum):
    CITIZEN = "citizen"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    citizen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    state: Mapped[ConversationState] = mapped_column(
        Enum(ConversationState), nullable=False, default=ConversationState.ACTIVE
    )
    current_round: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    message_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["ConversationSession"] = relationship(back_populates="messages")
