import uuid
import pytest
from app.domain.consolidation import IssueConsolidator


class TestIssueConsolidator:
    def setup_method(self):
        self.consolidator = IssueConsolidator()

    def test_same_category_same_location_matches(self):
        cluster = {
            "id": uuid.uuid4(),
            "category": "water_supply",
            "subcategory": "no_water",
            "latitude": 28.6139,
            "longitude": 77.2090,
        }
        candidates = self.consolidator.find_matching_clusters(
            category="water_supply",
            subcategory="no_water",
            latitude=28.6140,
            longitude=77.2091,
            semantic_embedding=None,
            existing_clusters=[cluster],
        )
        assert len(candidates) == 1
        assert candidates[0].similarity_score >= 0.7

    def test_different_category_different_location_no_match(self):
        cluster = {
            "id": uuid.uuid4(),
            "category": "road_damage",
            "subcategory": "pothole",
            "latitude": 19.0760,
            "longitude": 72.8777,
        }
        candidates = self.consolidator.find_matching_clusters(
            category="water_supply",
            subcategory="no_water",
            latitude=28.6139,
            longitude=77.2090,
            semantic_embedding=None,
            existing_clusters=[cluster],
        )
        assert len(candidates) == 0

    def test_same_category_far_location_no_match(self):
        cluster = {
            "id": uuid.uuid4(),
            "category": "water_supply",
            "subcategory": "no_water",
            "latitude": 19.0760,
            "longitude": 72.8777,
        }
        candidates = self.consolidator.find_matching_clusters(
            category="water_supply",
            subcategory="no_water",
            latitude=28.6139,
            longitude=77.2090,
            semantic_embedding=None,
            existing_clusters=[cluster],
        )
        assert len(candidates) == 0

    def test_empty_clusters_returns_no_candidates(self):
        candidates = self.consolidator.find_matching_clusters(
            category="water_supply",
            subcategory="no_water",
            latitude=28.6139,
            longitude=77.2090,
            semantic_embedding=None,
            existing_clusters=[],
        )
        assert len(candidates) == 0

    def test_should_create_new_cluster_when_no_candidates(self):
        assert self.consolidator.should_create_new_cluster([]) is True

    def test_should_create_new_cluster_when_low_score(self):
        from app.domain.consolidation import ConsolidationCandidate
        candidate = ConsolidationCandidate(
            cluster_id=uuid.uuid4(),
            similarity_score=0.5,
            geographic_proximity=100,
            category_match=True,
            semantic_similarity=0.5,
        )
        assert self.consolidator.should_create_new_cluster([candidate]) is True

    def test_should_not_create_new_cluster_when_high_score(self):
        from app.domain.consolidation import ConsolidationCandidate
        candidate = ConsolidationCandidate(
            cluster_id=uuid.uuid4(),
            similarity_score=0.9,
            geographic_proximity=100,
            category_match=True,
            semantic_similarity=0.9,
        )
        assert self.consolidator.should_create_new_cluster([candidate]) is False
