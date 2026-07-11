from dataclasses import dataclass


@dataclass
class PrioritiesQuery:
    constituency: str | None = None
    category: str | None = None
    min_level: str | None = None
    skip: int = 0
    limit: int = 100
