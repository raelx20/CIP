from abc import ABC, abstractmethod
from typing import Any


class PlacesProvider(ABC):
    @abstractmethod
    async def search_places(
        self,
        query: str,
        location: tuple[float, float] | None = None,
        radius: int | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_place_details(
        self,
        place_id: str,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
