import uuid
from datetime import datetime, timezone

from app.common.logger import get_logger
from app.domain.conversation.value_objects import ConversationState, MessageRole
from app.domain.submission.value_objects import SubmissionStatus
from app.prompts.citizen_system import CITIZEN_SYSTEM_PROMPT
from app.prompts.multilingual import MULTILINGUAL_INSTRUCTIONS

logger = get_logger()


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
        history: list[dict] | None = None,
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

            # Build conversation context from history
            conversation_context = ""
            if history:
                conversation_context = "Previous conversation:\n"
                for msg in history:
                    role_label = "Citizen" if msg.get("role") == "citizen" else "Assistant"
                    conversation_context += f"{role_label}: {msg.get('content', '')}\n"
                conversation_context += "\n"

            prompt = f"{conversation_context}Citizen message: {message}\n\nRespond naturally, empathetically, and helpfully. If the citizen has already provided context in previous messages, acknowledge it and build on it. Ask for location details only if not already provided."

            ai_content = await llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500,
            )
        except Exception as e:
            logger.error("LLM call failed: {} - {}", type(e).__name__, str(e))
            ai_content = (
                "I'm sorry, the AI assistant is temporarily unavailable. "
                "Your concern has been noted. Please try again in a moment, "
                "or use the 'Submit Issue' page to submit your issue directly."
            )

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
            logger.error("LLM copilot call failed: {} - {}", type(e).__name__, str(e))
            answer = f"The AI copilot is temporarily unavailable. Please try again in a moment. Your query: {query}"

        return {
            "answer": answer,
            "citations": [],
            "uncertainty": None,
            "sources_used": ["internal_database"],
        }
