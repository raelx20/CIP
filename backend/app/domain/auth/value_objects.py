import enum
from dataclasses import dataclass


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    MP = "mp"
    OFFICER = "officer"
    ADMIN = "admin"


@dataclass(frozen=True)
class Permission:
    resource: str
    action: str

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"


ROLE_PERMISSIONS: dict[UserRole, list[Permission]] = {
    UserRole.CITIZEN: [
        Permission("submissions", "create"),
        Permission("submissions", "read_own"),
        Permission("conversations", "participate"),
    ],
    UserRole.MP: [
        Permission("submissions", "read_constituency"),
        Permission("issues", "read"),
        Permission("priorities", "read"),
        Permission("hotspots", "read"),
        Permission("copilot", "use"),
        Permission("reviews", "read"),
    ],
    UserRole.OFFICER: [
        Permission("submissions", "read_assigned"),
        Permission("reviews", "create"),
        Permission("reviews", "update"),
        Permission("evidence", "add"),
    ],
    UserRole.ADMIN: [
        Permission("submissions", "read_all"),
        Permission("issues", "manage"),
        Permission("priorities", "manage"),
        Permission("users", "manage"),
        Permission("config", "manage"),
        Permission("reviews", "manage"),
    ],
}
