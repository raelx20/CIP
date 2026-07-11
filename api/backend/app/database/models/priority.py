import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PriorityLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class ThreatDimension(str, enum.Enum):
    POLITICAL_IMPACT = "political_impact"
    SOCIAL_IMPACT = "social_impact"
    CASTE_DYNAMICS = "caste_dynamics"
    SCIENTIFIC_BASIS = "scientific_basis"
    NATURAL_RISK = "natural_risk"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    INNOVATION_POTENTIAL = "innovation_potential"
    SOCIETAL_BENEFIT = "societal_benefit"
    HUMANITARIAN_CONCERN = "humanitarian_concern"
    MORAL_ETHICAL_WEIGHT = "moral_ethical_weight"
    RELIGIOUS_SENSITIVITY = "religious_sensitivity"
    FINANCIAL_IMPACT = "financial_impact"
    FUTURISTIC_LONGTERM = "futuristic_longterm"
    EDUCATIONAL_VALUE = "educational_value"
    HISTORICAL_SIGNIFICANCE = "historical_significance"
    SENTIMENTAL_EMOTIONAL = "sentimental_emotional"
    ADMINISTRATIVE_RISK = "administrative_risk"
    PUBLIC_CRITICISM_RISK = "public_criticism_risk"
    LEGAL_COMPLIANCE_RISK = "legal_compliance_risk"
    IMPLEMENTATION_RISK = "implementation_risk"


class PriorityAssessment(Base):
    __tablename__ = "priority_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_clusters.id"), nullable=False
    )
    final_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority_level: Mapped[PriorityLevel] = mapped_column(
        Enum(PriorityLevel), nullable=False, default=PriorityLevel.MEDIUM
    )
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scoring_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    weights: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    bonuses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    penalties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    uncertainties: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    evidence_references: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    calculation_timestamp: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PriorityScoreComponent(Base):
    __tablename__ = "priority_score_components"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("priority_assessments.id"), nullable=False
    )
    dimension: Mapped[ThreatDimension] = mapped_column(
        Enum(ThreatDimension), nullable=False
    )
    raw_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    normalized_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
