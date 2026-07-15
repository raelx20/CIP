import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str
    original_content: str | None = None
    detected_language: str | None = None
    timestamp: datetime | None = None
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    message: ChatMessage
    submission_id: uuid.UUID | None = None
    status: str | None = None
    requires_clarification: bool = False
    clarification_questions: list[str] = []


class ConversationHistory(BaseModel):
    session_id: uuid.UUID
    messages: list[ChatMessage]
    state: str
    current_round: int
    max_rounds: int
    language: str | None = None
