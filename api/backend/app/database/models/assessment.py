import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CaseAssessment(Base):
    __tablename__ = "case_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    primary_issue: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_infrastructure: Mapped[str | None] = mapped_column(String(255), nullable=True)
    candidate_departments: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    issue_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity_indicators: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    urgency_indicators: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    people_affected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    households_affected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vulnerable_groups: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    health_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    mobility_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    economic_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    environmental_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_disruption: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_conditions: Mapped[bool | None] = mapped_column(nullable=True)
    alternatives_available: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_information: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    contradictions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ambiguity: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    alternative_interpretations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    fact_inference_map: Mapped[dict | None] = mapped_column("fact_inference_map", JSONB, nullable=True)
    extraction_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
