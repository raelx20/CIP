from typing import Any

from app.contracts.llm import LLMProvider
from app.contracts.translator import Translator


LANGUAGE_NAMES = {
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


class LLMTranslator(Translator):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str = "en",
        **kwargs,
    ) -> str:
        source_name = LANGUAGE_NAMES.get(source_language, source_language)
        target_name = LANGUAGE_NAMES.get(target_language, target_language)

        prompt = f"""Translate the following text from {source_name} to {target_language}.
Preserve the original meaning and tone. Be natural in {target_name}.

Text to translate:
{text}"""

        return await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000,
        )

    async def detect_and_translate(
        self,
        text: str,
        target_language: str = "en",
        **kwargs,
    ) -> dict[str, Any]:
        prompt = f"""Detect the language of this text and translate it to {target_language}.
Respond with JSON: {{"detected_language": "xx", "translation": "translated text", "confidence": 0.95}}

Text:
{text[:1000]}"""

        response = await self.llm.generate_structured(
            prompt=prompt,
            schema={
                "detected_language": "string",
                "translation": "string",
                "confidence": "number",
            },
            temperature=0.3,
        )

        if "error" in response:
            return {
                "detected_language": "en",
                "translation": text,
                "confidence": 0.5,
            }

        return response

    def health_check(self) -> bool:
        return self.llm.health_check()
