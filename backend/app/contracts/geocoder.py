from abc import ABC, abstractmethod
from typing import Any


class GeocoderProvider(ABC):
    @abstractmethod
    async def geocode(
        self,
        address: str,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
