from dataclasses import dataclass


@dataclass
class DashboardQuery:
    constituency: str | None = None
    category: str | None = None
    time_window_days: int | None = None
