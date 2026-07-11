import enum
from dataclasses import dataclass


class LocationSource(str, enum.Enum):
    GPS = "gps"
    MAP_PIN = "map_pin"
    TYPED_ADDRESS = "typed_address"
    SPOKEN_ADDRESS = "spoken_address"
    EXTRACTED_TEXT = "extracted_text"
    MEDIA_METADATA = "media_metadata"
    OFFICER_VERIFICATION = "officer_verification"


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class Address:
    formatted: str
    landmark: str | None = None
    village: str | None = None
    ward: str | None = None
    municipality: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    postal_code: str | None = None
    constituency: str | None = None


@dataclass(frozen=True)
class LocationConsistency:
    city_match: bool | None = None
    district_match: bool | None = None
    constituency_match: bool | None = None
    distance_meters: float | None = None
    consistency_score: float | None = None
