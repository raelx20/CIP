import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ClusterLifecycleState(str, enum.Enum):
    NEW = "new"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssueCluster(Base):
    __tablename__ = "issue_clusters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    formatted_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    geographic_extent: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    administrative_areas: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    raw_submission_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trusted_demand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    suspicious_demand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    affected_population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    urgency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    persistence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    demand_velocity: Mapped[float | None] = mapped_column(Float, nullable=True)
    lifecycle_state: Mapped[ClusterLifecycleState] = mapped_column(
        Enum(ClusterLifecycleState), nullable=False, default=ClusterLifecycleState.NEW
    )
    supporting_evidence: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    contradictory_evidence: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    first_reported: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    latest_report: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memberships: Mapped[list["IssueClusterMembership"]] = relationship(
        back_populates="cluster", cascade="all, delete-orphan"
    )


class IssueClusterMembership(Base):
    __tablename__ = "issue_cluster_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_clusters.id"), nullable=False
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_primary: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    cluster: Mapped["IssueCluster"] = relationship(back_populates="memberships")
