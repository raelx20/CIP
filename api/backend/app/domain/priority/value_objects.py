import enum
from dataclasses import dataclass


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


@dataclass(frozen=True)
class ScoreComponent:
    dimension: ThreatDimension
    raw_value: float
    normalized_value: float
    weight: float
    weighted_score: float
    description: str | None = None

    def __post_init__(self):
        if not (0 <= self.normalized_value <= 1):
            raise ValueError(f"Normalized value must be between 0 and 1: {self.normalized_value}")
        if not (0 <= self.weight <= 1):
            raise ValueError(f"Weight must be between 0 and 1: {self.weight}")


@dataclass(frozen=True)
class PriorityScore:
    final_score: float
    priority_level: PriorityLevel
    components: list[ScoreComponent]
    scoring_version: str
    reasoning: str | None = None
