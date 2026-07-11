import math
from dataclasses import dataclass

from app.domain.location.value_objects import Coordinates, LocationConsistency


class LocationComparator:
    EARTH_RADIUS_METERS = 6371000

    def compare_locations(
        self,
        sender_coords: Coordinates | None,
        issue_coords: Coordinates | None,
        sender_city: str | None = None,
        issue_city: str | None = None,
        sender_district: str | None = None,
        issue_district: str | None = None,
        sender_constituency: str | None = None,
        issue_constituency: str | None = None,
    ) -> LocationConsistency:
        distance = None
        if sender_coords and issue_coords:
            distance = self._calculate_distance(sender_coords, issue_coords)

        city_match = self._normalize_match(sender_city, issue_city)
        district_match = self._normalize_match(sender_district, issue_district)
        constituency_match = self._normalize_match(sender_constituency, issue_constituency)

        consistency_score = self._calculate_consistency_score(
            city_match=city_match,
            district_match=district_match,
            constituency_match=constituency_match,
            distance_meters=distance,
        )

        return LocationConsistency(
            city_match=city_match,
            district_match=district_match,
            constituency_match=constituency_match,
            distance_meters=distance,
            consistency_score=consistency_score,
        )

    def _calculate_distance(self, coord1: Coordinates, coord2: Coordinates) -> float:
        lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
        lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS_METERS * c

    def _normalize_match(self, value1: str | None, value2: str | None) -> bool | None:
        if not value1 or not value2:
            return None
        return value1.strip().lower() == value2.strip().lower()

    def _calculate_consistency_score(
        self,
        city_match: bool | None,
        district_match: bool | None,
        constituency_match: bool | None,
        distance_meters: float | None,
    ) -> float:
        score = 0.5

        if city_match is True:
            score += 0.2
        elif city_match is False:
            score -= 0.2

        if district_match is True:
            score += 0.15
        elif district_match is False:
            score -= 0.15

        if constituency_match is True:
            score += 0.15
        elif constituency_match is False:
            score -= 0.15

        if distance_meters is not None:
            if distance_meters < 1000:
                score += 0.1
            elif distance_meters < 5000:
                score += 0.05
            elif distance_meters > 50000:
                score -= 0.2
            elif distance_meters > 100000:
                score -= 0.3

        return max(0.0, min(1.0, score))

    def is_gps_valid(self, coords: Coordinates) -> bool:
        if not (-90 <= coords.latitude <= 90):
            return False
        if not (-180 <= coords.longitude <= 180):
            return False
        if coords.latitude == 0.0 and coords.longitude == 0.0:
            return False
        return True
