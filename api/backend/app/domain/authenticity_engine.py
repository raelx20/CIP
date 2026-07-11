from dataclasses import dataclass

from app.domain.authenticity.value_objects import (
    AuthenticityScore,
    AuthenticityStatus,
    DemandWeight,
    SignalType,
)


@dataclass
class SignalWeight:
    geographic_consistency: float = 0.15
    location_validity: float = 0.10
    clarification_consistency: float = 0.12
    internal_contradiction: float = 0.10
    duplicate_behavior: float = 0.08
    submission_velocity: float = 0.06
    media_metadata: float = 0.05
    media_similarity: float = 0.05
    semantic_similarity: float = 0.08
    coordinated_pattern: float = 0.07
    citizen_corroboration: float = 0.06
    public_dataset_consistency: float = 0.04
    news_corroboration: float = 0.02
    officer_verification: float = 0.02


DEFAULT_SIGNAL_WEIGHTS = SignalWeight()


class AuthenticityEngine:
    def __init__(self, signal_weights: SignalWeight | None = None):
        self.signal_weights = signal_weights or DEFAULT_SIGNAL_WEIGHTS
        self.scoring_version = "1.0"

    def assess_authenticity(
        self,
        signals: dict[SignalType, float],
        gps_permission_granted: bool | None = None,
        sender_issue_consistency: float | None = None,
    ) -> AuthenticityScore:
        component_scores = {}
        total_score = 0.0
        total_weight = 0.0

        for signal_type, signal_value in signals.items():
            weight = getattr(self.signal_weights, signal_type.value, 0.05)
            normalized_value = min(max(signal_value, 0.0), 1.0)
            weighted_score = normalized_value * weight

            component_scores[signal_type.value] = {
                "raw": signal_value,
                "normalized": normalized_value,
                "weight": weight,
                "weighted": weighted_score,
            }

            total_score += weighted_score
            total_weight += weight

        if total_weight > 0:
            authenticity_score = total_score / total_weight
        else:
            authenticity_score = 0.5

        if gps_permission_granted is False:
            authenticity_score *= 0.95

        status = self._score_to_status(authenticity_score)
        confidence = self._calculate_confidence(signals, component_scores)
        review_required = self._needs_review(authenticity_score, signals)

        return AuthenticityScore(
            score=authenticity_score,
            status=status,
            confidence=confidence,
            review_required=review_required,
            scoring_version=self.scoring_version,
        )

    def calculate_demand_weight(
        self,
        trusted_signals: dict[SignalType, float],
        suspicious_signals: dict[SignalType, float],
    ) -> DemandWeight:
        trusted_weight = sum(trusted_signals.values()) / max(len(trusted_signals), 1)
        suspicious_weight = sum(suspicious_signals.values()) / max(len(suspicious_signals), 1)
        total_weight = trusted_weight + (1 - suspicious_weight)

        return DemandWeight(
            trusted=trusted_weight,
            suspicious=suspicious_weight,
            total=total_weight,
        )

    def _score_to_status(self, score: float) -> AuthenticityStatus:
        if score >= 0.8:
            return AuthenticityStatus.GENUINE
        elif score >= 0.65:
            return AuthenticityStatus.LIKELY_GENUINE
        elif score >= 0.45:
            return AuthenticityStatus.UNCERTAIN
        elif score >= 0.3:
            return AuthenticityStatus.SUSPICIOUS
        elif score >= 0.15:
            return AuthenticityStatus.LIKELY_FRAUDULENT
        else:
            return AuthenticityStatus.FRAUDULENT

    def _calculate_confidence(
        self,
        signals: dict[SignalType, float],
        component_scores: dict,
    ) -> float:
        if not signals:
            return 0.0

        signal_count = len(signals)
        max_possible = len(SignalType)
        coverage = signal_count / max_possible

        value_variance = sum(
            (v - 0.5) ** 2 for v in signals.values()
        ) / max(len(signals), 1)
        consistency = 1.0 - (value_variance * 2)

        return min((coverage * 0.6 + consistency * 0.4), 1.0)

    def _needs_review(
        self,
        score: float,
        signals: dict[SignalType, float],
    ) -> bool:
        if score < 0.3:
            return True
        if score > 0.7:
            return False

        has_suspicious = any(
            signals.get(st, 0) < 0.3
            for st in [
                SignalType.GEOGRAPHIC_CONSISTENCY,
                SignalType.CLARIFICATION_CONSISTENCY,
                SignalType.INTERNAL_CONTRADICTION,
            ]
        )
        return has_suspicious
