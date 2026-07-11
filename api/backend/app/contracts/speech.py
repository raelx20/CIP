from abc import ABC, abstractmethod
from typing import Any


class SpeechToText(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def transcribe_file(
        self,
        file_path: str,
        language: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
