from abc import ABC, abstractmethod
from typing import Any


class Translator(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str = "en",
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def detect_and_translate(
        self,
        text: str,
        target_language: str = "en",
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
