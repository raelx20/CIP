import uuid
from dataclasses import dataclass


@dataclass
class ConsolidationCandidate:
    cluster_id: uuid.UUID
    similarity_score: float
    geographic_proximity: float
    category_match: bool
    semantic_similarity: float


class IssueConsolidator:
    SEMANTIC_SIMILARITY_THRESHOLD = 0.7
    GEOGRAPHIC_PROXIMITY_THRESHOLD = 5000  # meters
    CATEGORY_MATCH_REQUIRED = True

    def find_matching_clusters(
        self,
        category: str,
        subcategory: str | None,
        latitude: float | None,
        longitude: float | None,
        semantic_embedding: list[float] | None,
        existing_clusters: list[dict],
    ) -> list[ConsolidationCandidate]:
        candidates = []

        for cluster in existing_clusters:
            score = self._calculate_match_score(
                category=category,
                subcategory=subcategory,
                latitude=latitude,
                longitude=longitude,
                cluster=cluster,
            )

            if score >= self.SEMANTIC_SIMILARITY_THRESHOLD:
                candidates.append(
                    ConsolidationCandidate(
                        cluster_id=cluster["id"],
                        similarity_score=score,
                        geographic_proximity=cluster.get("distance", 0),
                        category_match=category.lower() == cluster.get("category", "").lower(),
                        semantic_similarity=score,
                    )
                )

        candidates.sort(key=lambda c: c.similarity_score, reverse=True)
        return candidates

    def _calculate_match_score(
        self,
        category: str,
        subcategory: str | None,
        latitude: float | None,
        longitude: float | None,
        cluster: dict,
    ) -> float:
        score = 0.0

        if category.lower() == cluster.get("category", "").lower():
            score += 0.4

        if subcategory and subcategory.lower() == cluster.get("subcategory", "").lower():
            score += 0.2

        if latitude and longitude and cluster.get("latitude") and cluster.get("longitude"):
            distance = self._haversine_distance(
                latitude, longitude,
                cluster["latitude"], cluster["longitude"]
            )
            if distance < self.GEOGRAPHIC_PROXIMITY_THRESHOLD:
                proximity_score = 1.0 - (distance / self.GEOGRAPHIC_PROXIMITY_THRESHOLD)
                score += proximity_score * 0.3

        if cluster.get("title_similarity"):
            score += cluster["title_similarity"] * 0.1

        return min(score, 1.0)

    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        import math

        R = 6371000

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def should_create_new_cluster(
        self,
        candidates: list[ConsolidationCandidate],
        threshold: float = 0.8,
    ) -> bool:
        if not candidates:
            return True
        return candidates[0].similarity_score < threshold
