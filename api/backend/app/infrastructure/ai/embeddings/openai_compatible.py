from app.contracts.llm import LLMProvider


class OpenAICompatibleEmbeddings:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def embed(self, text: str) -> list[float]:
        return await self.llm.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return await self.llm.embed_batch(texts)

    def health_check(self) -> bool:
        return self.llm.health_check()
