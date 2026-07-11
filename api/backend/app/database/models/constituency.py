import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.database.base import Base


class Constituency(Base):
    __tablename__ = "constituencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    district: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="lok_sabha"
    )  # 'lok_sabha' or 'vidhan_sabha'
    ac_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pc_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    geom = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326), nullable=True
    )
    centroid_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroid_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
