import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class IssueClusterResponse(BaseModel):
    id: uuid.UUID
    title: str
    summary: str | None = None
    category: str
    subcategory: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    formatted_address: str | None = None
    raw_submission_count: int
    trusted_demand: float
    suspicious_demand: float
    affected_population: int | None = None
    severity: int | None = None
    urgency: int | None = None
    lifecycle_state: str
    confidence: float
    first_reported: datetime
    latest_report: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class IssueDetailResponse(IssueClusterResponse):
    administrative_areas: list[str] | None = None
    supporting_evidence: list[dict] | None = None
    contradictory_evidence: list[dict] | None = None
    demand_velocity: float | None = None
    persistence: str | None = None


class IssueListResponse(BaseModel):
    issues: list[IssueClusterResponse]
    total: int
    skip: int
    limit: int
