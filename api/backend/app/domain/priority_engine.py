from dataclasses import dataclass

from app.domain.priority.value_objects import (
    PriorityLevel,
    PriorityScore,
    ScoreComponent,
    ThreatDimension,
)


@dataclass
class PriorityWeights:
    political_impact: float = 0.08
    social_impact: float = 0.07
    caste_dynamics: float = 0.04
    scientific_basis: float = 0.04
    natural_risk: float = 0.06
    environmental_impact: float = 0.05
    innovation_potential: float = 0.03
    societal_benefit: float = 0.06
    humanitarian_concern: float = 0.08
    moral_ethical_weight: float = 0.04
    religious_sensitivity: float = 0.03
    financial_impact: float = 0.05
    futuristic_longterm: float = 0.04
    educational_value: float = 0.04
    historical_significance: float = 0.03
    sentimental_emotional: float = 0.04
    administrative_risk: float = 0.06
    public_criticism_risk: float = 0.07
    legal_compliance_risk: float = 0.05
    implementation_risk: float = 0.04

    def to_dict(self) -> dict[str, float]:
        return {
            "political_impact": self.political_impact,
            "social_impact": self.social_impact,
            "caste_dynamics": self.caste_dynamics,
            "scientific_basis": self.scientific_basis,
            "natural_risk": self.natural_risk,
            "environmental_impact": self.environmental_impact,
            "innovation_potential": self.innovation_potential,
            "societal_benefit": self.societal_benefit,
            "humanitarian_concern": self.humanitarian_concern,
            "moral_ethical_weight": self.moral_ethical_weight,
            "religious_sensitivity": self.religious_sensitivity,
            "financial_impact": self.financial_impact,
            "futuristic_longterm": self.futuristic_longterm,
            "educational_value": self.educational_value,
            "historical_significance": self.historical_significance,
            "sentimental_emotional": self.sentimental_emotional,
            "administrative_risk": self.administrative_risk,
            "public_criticism_risk": self.public_criticism_risk,
            "legal_compliance_risk": self.legal_compliance_risk,
            "implementation_risk": self.implementation_risk,
        }


DEFAULT_WEIGHTS = PriorityWeights()


class PriorityEngine:
    def __init__(self, weights: PriorityWeights | None = None):
        self.weights = weights or DEFAULT_WEIGHTS
        self.scoring_version = "1.0"

    def calculate_priority(
        self,
        dimension_scores: dict[ThreatDimension, float],
        submission_count: int = 1,
        urgency: int = 5,
        severity: int = 5,
    ) -> PriorityScore:
        components = []
        total_score = 0.0

        for dimension in ThreatDimension:
            raw_value = dimension_scores.get(dimension, 0.0)
            normalized_value = min(max(raw_value, 0.0), 1.0)
            weight = getattr(self.weights, dimension.value, 0.05)
            weighted_score = normalized_value * weight

            components.append(
                ScoreComponent(
                    dimension=dimension,
                    raw_value=raw_value,
                    normalized_value=normalized_value,
                    weight=weight,
                    weighted_score=weighted_score,
                )
            )
            total_score += weighted_score

        demand_factor = min(submission_count / 10, 1.0) * 0.1
        urgency_factor = (urgency / 10) * 0.1
        severity_factor = (severity / 10) * 0.1

        final_score = total_score + demand_factor + urgency_factor + severity_factor
        final_score = min(final_score, 1.0)

        priority_level = self._score_to_level(final_score)

        return PriorityScore(
            final_score=final_score,
            priority_level=priority_level,
            components=components,
            scoring_version=self.scoring_version,
        )

    def _score_to_level(self, score: float) -> PriorityLevel:
        if score >= 0.8:
            return PriorityLevel.CRITICAL
        elif score >= 0.6:
            return PriorityLevel.HIGH
        elif score >= 0.4:
            return PriorityLevel.MEDIUM
        elif score >= 0.2:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.DEFERRED

    def explain_score(self, priority_score: PriorityScore) -> str:
        explanations = []
        top_components = sorted(
            priority_score.components,
            key=lambda c: c.weighted_score,
            reverse=True,
        )[:5]

        for comp in top_components:
            explanations.append(
                f"- {comp.dimension.value}: {comp.normalized_value:.2f} "
                f"(weight: {comp.weight:.2f}, contribution: {comp.weighted_score:.3f})"
            )

        return (
            f"Priority Score: {priority_score.final_score:.3f} "
            f"({priority_score.priority_level.value})\n"
            f"Top contributing factors:\n" + "\n".join(explanations)
        )
