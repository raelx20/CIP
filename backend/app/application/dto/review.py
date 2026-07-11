import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewQueueItem(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    officer_id: uuid.UUID | None = None
    decision: str
    reason: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(approved|rejected|request_investigation|request_clarification|escalated)$")
    reason: str | None = Field(None, max_length=5000)
    corrections: dict | None = None


class ReviewDecisionResponse(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    officer_id: uuid.UUID
    decision: str
    reason: str | None = None
    created_at: datetime
    updated_at: datetime
