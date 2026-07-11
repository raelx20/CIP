import uuid
from typing import Any

from app.prompts.citizen_system import CITIZEN_SYSTEM_PROMPT
from app.prompts.multilingual import MULTILINGUAL_INSTRUCTIONS


async def generate_chat_response(payload: dict[str, Any]) -> dict[str, Any]:
    message = payload.get("message", "")
    detected_language = payload.get("detected_language", "en")
    conversation_history = payload.get("history", [])

    system_prompt = f"{CITIZEN_SYSTEM_PROMPT}\n\n{MULTILINGUAL_INSTRUCTIONS}"

    response = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": f"Thank you for sharing this with us. I understand your concern and I'm here to help. Could you please provide a bit more detail about the location of this issue?",
        "detected_language": detected_language,
        "metadata": {
            "tone": "empathetic",
            "emotion": "concerned",
        },
    }

    return response
