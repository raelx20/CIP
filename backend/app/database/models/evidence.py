import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EvidenceType(str, enum.Enum):
    CITIZEN_SUBMISSION = "citizen_submission"
    DEMOGRAPHIC = "demographic"
    INFRASTRUCTURE = "infrastructure"
    DEVELOPMENT_PLAN = "development_plan"
    PUBLIC_DATASET = "public_dataset"
    GOVERNMENT_DATASET = "government_dataset"
    HISTORICAL_RECORD = "historical_record"
    NEWS_ARTICLE = "news_article"
    OFFICER_VERIFICATION = "officer_verification"
    INDEPENDENT_EVIDENCE = "independent_evidence"


class EvidenceRelationshipType(str, enum.Enum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"
    UNVERIFIED = "unverified"


class ContextEvidence(Base):
    __tablename__ = "context_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_clusters.id"), nullable=False
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    retrieval_timestamp: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    publication_timestamp: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    freshness: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unverified")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    extracted_facts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    geographic_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    temporal_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    relationship_to_issue: Mapped[EvidenceRelationshipType] = mapped_column(
        Enum(EvidenceRelationshipType), nullable=False, default=EvidenceRelationshipType.UNVERIFIED
    )
    provider_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class EvidenceRelationship(Base):
    __tablename__ = "evidence_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    source_evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("context_evidence.id"), nullable=False
    )
    target_evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("context_evidence.id"), nullable=False
    )
    relationship_type: Mapped[EvidenceRelationshipType] = mapped_column(
        Enum(EvidenceRelationshipType), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
