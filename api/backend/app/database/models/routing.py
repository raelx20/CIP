import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DepartmentRouting(Base):
    __tablename__ = "department_routings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_clusters.id"), nullable=True
    )
    primary_department: Mapped[str] = mapped_column(String(255), nullable=False)
    alternative_departments: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    routing_reasons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    jurisdiction_uncertainty: Mapped[bool] = mapped_column(nullable=False, default=False)
    manual_review_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    routing_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
