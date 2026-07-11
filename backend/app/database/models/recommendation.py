import uuid
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_clusters.id"), nullable=False
    )
    priority_assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("priority_assessments.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    responsible_department_candidates: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    implementation_steps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    expected_outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_beneficiaries: Mapped[int | None] = mapped_column(Integer, nullable=True)
    supporting_evidence_refs: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    contradictory_evidence: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    dependencies: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    risks: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    uncertainties: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    alternative_actions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
