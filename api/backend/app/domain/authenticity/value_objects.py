import enum
from dataclasses import dataclass


class AuthenticityStatus(str, enum.Enum):
    GENUINE = "genuine"
    LIKELY_GENUINE = "likely_genuine"
    UNCERTAIN = "uncertain"
    SUSPICIOUS = "suspicious"
    LIKELY_FRAUDULENT = "likely_fraudulent"
    FRAUDULENT = "fraudulent"


class SignalType(str, enum.Enum):
    GEOGRAPHIC_CONSISTENCY = "geographic_consistency"
    LOCATION_VALIDITY = "location_validity"
    CLARIFICATION_CONSISTENCY = "clarification_consistency"
    INTERNAL_CONTRADICTION = "internal_contradiction"
    DUPLICATE_BEHAVIOR = "duplicate_behavior"
    SUBMISSION_VELOCITY = "submission_velocity"
    MEDIA_METADATA = "media_metadata"
    MEDIA_SIMILARITY = "media_similarity"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    COORDINATED_PATTERN = "coordinated_pattern"
    CITIZEN_CORROBORATION = "citizen_corroboration"
    PUBLIC_DATASET_CONSISTENCY = "public_dataset_consistency"
    NEWS_CORROBORATION = "news_corroboration"
    OFFICER_VERIFICATION = "officer_verification"


@dataclass(frozen=True)
class AuthenticityScore:
    score: float
    status: AuthenticityStatus
    confidence: float
    review_required: bool
    scoring_version: str

    def __post_init__(self):
        if not (0 <= self.score <= 1):
            raise ValueError(f"Score must be between 0 and 1: {self.score}")
        if not (0 <= self.confidence <= 1):
            raise ValueError(f"Confidence must be between 0 and 1: {self.confidence}")


@dataclass(frozen=True)
class DemandWeight:
    trusted: float
    suspicious: float
    total: float

    def __post_init__(self):
        if self.trusted < 0:
            raise ValueError(f"Trusted demand cannot be negative: {self.trusted}")
        if self.suspicious < 0:
            raise ValueError(f"Suspicious demand cannot be negative: {self.suspicious}")
