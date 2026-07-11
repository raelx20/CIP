import re
from typing import Any


class PrivacyService:
    GPS_RETENTION_HOURS = 24
    PII_FIELDS = [
        "email",
        "phone",
        "address",
        "sender_latitude",
        "sender_longitude",
        "sender_gps_accuracy",
    ]

    def mask_pii(self, data: dict[str, Any]) -> dict[str, Any]:
        masked = data.copy()

        for field in self.PII_FIELDS:
            if field in masked:
                if field == "email":
                    masked[field] = self._mask_email(masked[field])
                elif field == "phone":
                    masked[field] = self._mask_phone(masked[field])
                elif field in ("sender_latitude", "sender_longitude"):
                    masked[field] = self._mask_coordinates(masked[field])

        return masked

    def should_delete_gps(self, gps_timestamp: str | None, retention_hours: int | None = None) -> bool:
        if not gps_timestamp:
            return False

        from datetime import datetime, timezone, timedelta

        try:
            if gps_timestamp.endswith("Z"):
                gps_timestamp = gps_timestamp[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(gps_timestamp)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            retention = retention_hours or self.GPS_RETENTION_HOURS
            cutoff = datetime.now(timezone.utc) - timedelta(hours=retention)

            return timestamp < cutoff
        except (ValueError, TypeError):
            return False

    def sanitize_log_message(self, message: str) -> str:
        message = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', message)
        message = re.sub(r'\b\d{10}\b', '[PHONE]', message)
        message = re.sub(r'-?\d+\.\d{4,}', '[COORD]', message)
        return message

    def get_gps_deletion_candidates(self, submissions: list[dict]) -> list[dict]:
        candidates = []
        for sub in submissions:
            if self.should_delete_gps(sub.get("sender_gps_timestamp")):
                candidates.append({
                    "submission_id": sub["id"],
                    "reason": "GPS retention period exceeded",
                })
        return candidates

    def _mask_email(self, email: str) -> str:
        if not email or "@" not in email:
            return "[EMAIL]"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"

    def _mask_phone(self, phone: str) -> str:
        if not phone or len(phone) < 4:
            return "[PHONE]"
        return phone[:2] + "***" + phone[-2:]

    def _mask_coordinates(self, coord: float | None) -> float | None:
        if coord is None:
            return None
        return round(coord, 2)
