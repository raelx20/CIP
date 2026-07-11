from abc import ABC, abstractmethod
from typing import Any


class VisionOCR(ABC):
    @abstractmethod
    async def extract_text(
        self,
        image_data: bytes,
        language: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def extract_text_from_file(
        self,
        file_path: str,
        language: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
