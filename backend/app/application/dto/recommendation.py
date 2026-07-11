import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    cluster_id: uuid.UUID
    title: str
    recommended_action: str
    responsible_department_candidates: list[str] | None = None
    rationale: str | None = None
    implementation_steps: list[dict] | None = None
    expected_outcomes: str | None = None
    expected_beneficiaries: int | None = None
    supporting_evidence_refs: list[dict] | None = None
    contradictory_evidence: list[dict] | None = None
    dependencies: list[str] | None = None
    risks: list[str] | None = None
    uncertainties: list[str] | None = None
    confidence: float
    alternative_actions: list[dict] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
