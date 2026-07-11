import uuid
from datetime import datetime, timezone

from app.domain.submission.value_objects import SourceModality, SubmissionStatus


class IntakeWorkflow:
    async def process_text_input(
        self,
        citizen_id: uuid.UUID,
        content: str,
        source_channel: str = "api",
        language: str | None = None,
        gps_permission_granted: bool | None = None,
        sender_latitude: float | None = None,
        sender_longitude: float | None = None,
        sender_gps_accuracy: float | None = None,
    ) -> dict:
        submission_id = uuid.uuid4()

        submission = {
            "id": submission_id,
            "citizen_id": citizen_id,
            "status": SubmissionStatus.RECEIVED.value,
            "source_modality": SourceModality.TEXT.value,
            "source_channel": source_channel,
            "original_content": content,
            "normalized_content": None,
            "detected_language": language,
            "response_language": language,
            "category": None,
            "subcategory": None,
            "description": None,
            "severity": None,
            "urgency": None,
            "affected_population": None,
            "affected_households": None,
            "extraction_metadata": None,
            "processing_metadata": None,
            "gps_permission_granted": gps_permission_granted,
            "sender_latitude": sender_latitude,
            "sender_longitude": sender_longitude,
            "sender_gps_accuracy": sender_gps_accuracy,
            "sender_gps_timestamp": datetime.now(timezone.utc) if sender_latitude else None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        return submission

    async def process_voice_input(
        self,
        citizen_id: uuid.UUID,
        audio_data: bytes,
        language: str | None = None,
        **kwargs,
    ) -> dict:
        submission_id = uuid.uuid4()

        submission = {
            "id": submission_id,
            "citizen_id": citizen_id,
            "status": SubmissionStatus.RECEIVED.value,
            "source_modality": SourceModality.VOICE.value,
            "source_channel": "voice",
            "original_content": "[Voice input - pending transcription]",
            "normalized_content": None,
            "detected_language": language,
            "processing_metadata": {"audio_size": len(audio_data)},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        return submission

    async def process_image_input(
        self,
        citizen_id: uuid.UUID,
        image_data: bytes,
        filename: str | None = None,
        **kwargs,
    ) -> dict:
        submission_id = uuid.uuid4()

        submission = {
            "id": submission_id,
            "citizen_id": citizen_id,
            "status": SubmissionStatus.RECEIVED.value,
            "source_modality": SourceModality.IMAGE.value,
            "source_channel": "image",
            "original_content": "[Image input - pending OCR extraction]",
            "normalized_content": None,
            "processing_metadata": {"filename": filename, "image_size": len(image_data)},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        media = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "media_type": "image",
            "file_path": None,
            "original_filename": filename,
            "mime_type": "image/jpeg",
            "file_size": len(image_data),
            "created_at": datetime.now(timezone.utc),
        }

        return {"submission": submission, "media": media}
