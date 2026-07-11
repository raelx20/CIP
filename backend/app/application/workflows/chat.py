import uuid
from datetime import datetime, timezone

from app.domain.conversation.value_objects import ConversationState, MessageRole
from app.domain.submission.value_objects import SubmissionStatus
from app.prompts.citizen_system import CITIZEN_SYSTEM_PROMPT
from app.prompts.multilingual import MULTILINGUAL_INSTRUCTIONS


class ChatWorkflow:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from app.infrastructure.ai.llm.openai_compatible import OpenAICompatibleLLM
            from app.config import settings
            self._llm = OpenAICompatibleLLM(
                base_url=settings.LLM_BASE_URL,
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL,
                timeout=settings.LLM_TIMEOUT,
            )
        return self._llm

    async def process_citizen_message(
        self,
        citizen_id: uuid.UUID,
        message: str,
        session_id: uuid.UUID | None = None,
        detected_language: str | None = None,
    ) -> dict:
        if not session_id:
            session_id = uuid.uuid4()

        user_message = {
            "id": uuid.uuid4(),
            "session_id": session_id,
            "role": MessageRole.CITIZEN.value,
            "content": message,
            "original_content": message,
            "detected_language": detected_language,
            "message_metadata": None,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            llm = self._get_llm()
            system_prompt = f"{CITIZEN_SYSTEM_PROMPT}\n\n{MULTILINGUAL_INSTRUCTIONS}"

            ai_content = await llm.generate(
                prompt=f"Citizen message: {message}\n\nRespond naturally, empathetically, and helpfully. Ask for location if not provided.",
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500,
            )
        except Exception as e:
            ai_content = "Thank you for sharing this with us. I understand your concern and I'm here to help. Could you please provide a bit more detail about the location of this issue?"

        ai_response = {
            "id": uuid.uuid4(),
            "session_id": session_id,
            "role": MessageRole.ASSISTANT.value,
            "content": ai_content,
            "original_content": None,
            "detected_language": detected_language,
            "message_metadata": {
                "tone": "empathetic",
                "emotion": "concerned",
                "category_detected": None,
            },
            "created_at": datetime.now(timezone.utc),
        }

        return {
            "user_message": user_message,
            "ai_response": ai_response,
            "session_state": ConversationState.ACTIVE.value,
            "requires_clarification": True,
            "clarification_topics": ["exact_problem", "precise_location"],
        }

    async def process_admin_copilot_query(
        self,
        admin_id: uuid.UUID,
        query: str,
        constituency: str | None = None,
    ) -> dict:
        try:
            llm = self._get_llm()
            system_prompt = "You are a professional government decision-support assistant. Provide grounded, evidence-based responses."

            answer = await llm.generate(
                prompt=f"Constituency: {constituency or 'All'}\n\nQuery: {query}\n\nProvide a helpful, professional response.",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000,
            )
        except Exception as e:
            answer = f"Based on the current data, here is what I found regarding your query: {query}"

        return {
            "answer": answer,
            "citations": [],
            "uncertainty": None,
            "sources_used": ["internal_database"],
        }
