import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ScoreComponentResponse(BaseModel):
    dimension: str
    raw_value: float
    normalized_value: float
    weight: float
    weighted_score: float
    description: str | None = None


class PriorityResponse(BaseModel):
    id: uuid.UUID
    cluster_id: uuid.UUID
    final_score: float
    priority_level: str
    rank: int | None = None
    scoring_version: str
    components: list[ScoreComponentResponse] = []
    reasoning: str | None = None
    uncertainties: list[str] | None = None
    evidence_references: list[dict] | None = None
    calculation_timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriorityRankingResponse(BaseModel):
    rankings: list[PriorityResponse]
    total: int
    skip: int
    limit: int
    scoring_version: str


class ThreatAnalysisResponse(BaseModel):
    cluster_id: uuid.UUID
    threat_dimensions: dict[str, float]
    overall_threat_score: float
    highest_threat_dimension: str
    threat_alerts: list[str] = []
    recommendations: list[str] = []
