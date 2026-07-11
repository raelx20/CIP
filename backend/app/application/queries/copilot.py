from dataclasses import dataclass


@dataclass
class CopilotQuery:
    query: str
    constituency: str | None = None
    category_filter: str | None = None
    time_window_days: int | None = None
