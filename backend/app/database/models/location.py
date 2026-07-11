import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class LocationSource(str, enum.Enum):
    GPS = "gps"
    MAP_PIN = "map_pin"
    TYPED_ADDRESS = "typed_address"
    SPOKEN_ADDRESS = "spoken_address"
    EXTRACTED_TEXT = "extracted_text"
    MEDIA_METADATA = "media_metadata"
    OFFICER_VERIFICATION = "officer_verification"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    formatted_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    landmark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    village: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ward: Mapped[str | None] = mapped_column(String(255), nullable=True)
    municipality: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    constituency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[LocationSource] = mapped_column(
        Enum(LocationSource), nullable=False
    )
    precision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    geocoding_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    verification: Mapped["LocationVerification | None"] = relationship(back_populates="location", uselist=False)


class LocationVerification(Base):
    __tablename__ = "location_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    sender_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_district: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_constituency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_district: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_constituency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city_match: Mapped[bool | None] = mapped_column(nullable=True)
    district_match: Mapped[bool | None] = mapped_column(nullable=True)
    constituency_match: Mapped[bool | None] = mapped_column(nullable=True)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    verification_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    location: Mapped["Location"] = relationship(back_populates="verification")
