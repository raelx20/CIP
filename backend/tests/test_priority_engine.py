import pytest
from app.domain.priority_engine import PriorityEngine
from app.domain.priority.value_objects import ThreatDimension, PriorityLevel


class TestPriorityEngine:
    def setup_method(self):
        self.engine = PriorityEngine()

    def test_zero_inputs(self):
        result = self.engine.calculate_priority(
            dimension_scores={},
            submission_count=0,
            urgency=0,
            severity=0,
        )
        assert result.final_score >= 0.0
        assert result.final_score <= 1.0
        assert isinstance(result.priority_level, PriorityLevel)

    def test_maximum_inputs(self):
        scores = {d: 1.0 for d in ThreatDimension}
        result = self.engine.calculate_priority(
            dimension_scores=scores,
            submission_count=100,
            urgency=10,
            severity=10,
        )
        assert result.final_score > 0.5
        assert isinstance(result.priority_level, PriorityLevel)

    def test_missing_inputs_use_defaults(self):
        result = self.engine.calculate_priority(dimension_scores={})
        assert result.final_score >= 0.0
        assert isinstance(result.priority_level, PriorityLevel)

    def test_high_dimensions_beat_low(self):
        high_scores = {
            ThreatDimension.HUMANITARIAN_CONCERN: 1.0,
            ThreatDimension.POLITICAL_IMPACT: 1.0,
        }
        high_result = self.engine.calculate_priority(dimension_scores=high_scores)
        low_result = self.engine.calculate_priority(dimension_scores={})
        assert high_result.final_score >= low_result.final_score

    def test_score_bounded(self):
        scores = {d: 999.0 for d in ThreatDimension}
        result = self.engine.calculate_priority(dimension_scores=scores)
        assert 0.0 <= result.final_score <= 1.0

    def test_explain_score(self):
        scores = {ThreatDimension.HUMANITARIAN_CONCERN: 0.8}
        result = self.engine.calculate_priority(dimension_scores=scores)
        explanation = self.engine.explain_score(result)
        assert "Priority Score" in explanation
        assert result.priority_level.value in explanation

    def test_scoring_version(self):
        result = self.engine.calculate_priority(dimension_scores={})
        assert result.scoring_version == "1.0"
