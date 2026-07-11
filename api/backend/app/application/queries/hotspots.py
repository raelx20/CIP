from dataclasses import dataclass


@dataclass
class HotspotsQuery:
    constituency: str | None = None
    category: str | None = None
    min_submissions: int = 3
    skip: int = 0
    limit: int = 100
