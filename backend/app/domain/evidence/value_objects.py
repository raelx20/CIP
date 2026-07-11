import enum
from dataclasses import dataclass


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


@dataclass(frozen=True)
class Provenance:
    source_type: EvidenceType
    source_name: str
    source_reference: str | None = None
    source_url: str | None = None
    retrieval_timestamp: str | None = None
    publication_timestamp: str | None = None
    freshness: str | None = None
    verification_status: str = "unverified"
