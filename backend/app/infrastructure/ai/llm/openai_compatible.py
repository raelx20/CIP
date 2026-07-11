import json
from typing import Any

import httpx

from app.contracts.llm import LLMProvider
from app.config import settings


class OpenAICompatibleLLM(LLMProvider):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = base_url or "http://localhost:8000/v1"
        self.api_key = api_key or "no-key"
        self.model = model or "qwen3-32b"
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> dict[str, Any]:
        structured_prompt = f"""{prompt}

You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with the JSON object, no other text."""

        response_text = await self.generate(
            prompt=structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        try:
            json_str = response_text.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("\n", 1)[1]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse structured response", "raw": response_text}

    async def embed(
        self,
        text: str,
        **kwargs,
    ) -> list[float]:
        response = await self.client.post(
            "/embeddings",
            json={
                "model": f"{self.model}-embed",
                "input": text,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

    async def embed_batch(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        response = await self.client.post(
            "/embeddings",
            json={
                "model": f"{self.model}-embed",
                "input": texts,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    def health_check(self) -> bool:
        try:
            response = self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
