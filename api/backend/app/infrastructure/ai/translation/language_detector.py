import json
from typing import Any

from app.contracts.language_detector import LanguageDetector
from app.contracts.llm import LLMProvider


SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "or": "Odia",
    "bn": "Bengali",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "as": "Assamese",
}


class LLLanguageDetector(LanguageDetector):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def detect(self, text: str, **kwargs) -> dict[str, Any]:
        prompt = f"""Detect the language of the following text. 
Respond with JSON: {{"language_code": "xx", "language_name": "Name", "confidence": 0.95, "is_code_mixed": false, "detected_scripts": ["Latin"]}}

Text: {text[:500]}"""

        response = await self.llm.generate_structured(
            prompt=prompt,
            schema={
                "language_code": "string",
                "language_name": "string",
                "confidence": "number",
                "is_code_mixed": "boolean",
                "detected_scripts": "array",
            },
            temperature=0.1,
        )

        if "error" in response:
            return {
                "language_code": "en",
                "language_name": "English",
                "confidence": 0.5,
                "is_code_mixed": False,
                "detected_scripts": ["Latin"],
            }

        return response

    async def detect_batch(self, texts: list[str], **kwargs) -> list[dict[str, Any]]:
        results = []
        for text in texts:
            result = await self.detect(text, **kwargs)
            results.append(result)
        return results

    def health_check(self) -> bool:
        return self.llm.health_check()
