import uuid
from pydantic import BaseModel, Field


class CopilotQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    constituency: str | None = None
    category_filter: str | None = None
    time_window_days: int | None = None


class CopilotCitation(BaseModel):
    evidence_id: uuid.UUID
    source_type: str
    source_name: str
    excerpt: str
    confidence: float


class CopilotResponse(BaseModel):
    answer: str
    citations: list[CopilotCitation] = []
    uncertainty: str | None = None
    sources_used: list[str] = []
