from dataclasses import dataclass


@dataclass
class IssuesQuery:
    constituency: str | None = None
    category: str | None = None
    status: str | None = None
    min_severity: int | None = None
    min_urgency: int | None = None
    skip: int = 0
    limit: int = 100
