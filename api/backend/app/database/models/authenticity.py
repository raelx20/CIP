import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuthenticityStatus(str, enum.Enum):
    GENUINE = "genuine"
    LIKELY_GENUINE = "likely_genuine"
    UNCERTAIN = "uncertain"
    SUSPICIOUS = "suspicious"
    LIKELY_FRAUDULENT = "likely_fraudulent"
    FRAUDULENT = "fraudulent"


class AuthenticityAssessment(Base):
    __tablename__ = "authenticity_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    authenticity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    authenticity_status: Mapped[AuthenticityStatus] = mapped_column(
        Enum(AuthenticityStatus), nullable=False, default=AuthenticityStatus.UNCERTAIN
    )
    demand_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    component_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    signals: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    reasons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    uncertainties: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    scoring_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    calculation_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    signals_list: Mapped[list["AuthenticitySignal"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class AuthenticitySignal(Base):
    __tablename__ = "authenticity_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("authenticity_assessments.id"), nullable=False
    )
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    assessment: Mapped["AuthenticityAssessment"] = relationship(back_populates="signals_list")
