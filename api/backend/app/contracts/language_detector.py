from abc import ABC, abstractmethod
from typing import Any


class LanguageDetector(ABC):
    @abstractmethod
    async def detect(
        self,
        text: str,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def detect_batch(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
