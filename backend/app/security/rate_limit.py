import time
from collections import defaultdict

from app.domain.auth.value_objects import UserRole


class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, role: UserRole | None = None) -> bool:
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        self.requests[key] = [
            t for t in self.requests[key] if t > hour_ago
        ]

        recent_minute = [t for t in self.requests[key] if t > minute_ago]
        recent_hour = self.requests[key]

        role_limits = {
            UserRole.CITIZEN: (30, 500),
            UserRole.MP: (120, 2000),
            UserRole.OFFICER: (120, 2000),
            UserRole.ADMIN: (300, 5000),
        }

        minute_limit, hour_limit = role_limits.get(
            role, (self.requests_per_minute, self.requests_per_hour)
        )

        if len(recent_minute) >= minute_limit:
            return False
        if len(recent_hour) >= hour_limit:
            return False

        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str, role: UserRole | None = None) -> dict[str, int]:
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        recent_minute = [t for t in self.requests.get(key, []) if t > minute_ago]
        recent_hour = [t for t in self.requests.get(key, []) if t > hour_ago]

        role_limits = {
            UserRole.CITIZEN: (30, 500),
            UserRole.MP: (120, 2000),
            UserRole.OFFICER: (120, 2000),
            UserRole.ADMIN: (300, 5000),
        }

        minute_limit, hour_limit = role_limits.get(
            role, (self.requests_per_minute, self.requests_per_hour)
        )

        return {
            "minute_remaining": max(0, minute_limit - len(recent_minute)),
            "hour_remaining": max(0, hour_limit - len(recent_hour)),
        }
