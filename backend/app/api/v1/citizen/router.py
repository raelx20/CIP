import uuid
from fastapi import APIRouter, HTTPException, status

from app.application.dto.submission import SubmissionCreate, SubmissionResponse
from app.application.dto.chat import ChatMessage, ChatResponse, ConversationHistory
from app.api.v1.citizen.my_issues import router as my_issues_router

router = APIRouter()

router.include_router(my_issues_router)


@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(request: SubmissionCreate):
    """Create a new citizen submission."""
    from app.application.workflows.intake import IntakeWorkflow
    from app.infrastructure.database.repositories.submission import SubmissionRepository
    from app.database.session import AsyncSessionLocal

    workflow = IntakeWorkflow()

    submission_data = await workflow.process_text_input(
        citizen_id=request.citizen_id,
        content=request.content,
        source_channel=request.source_channel,
        language=request.language,
        gps_permission_granted=request.gps_permission_granted,
        sender_latitude=request.sender_latitude,
        sender_longitude=request.sender_longitude,
        sender_gps_accuracy=request.sender_gps_accuracy,
    )

    async with AsyncSessionLocal() as session:
        repo = SubmissionRepository(session)
        submission = await repo.create(submission_data)

        return SubmissionResponse(
            id=submission.id,
            status=submission.status.value,
            source_modality=submission.source_modality.value,
            original_content=submission.original_content,
            normalized_content=submission.normalized_content,
            detected_language=submission.detected_language,
            category=submission.category,
            subcategory=submission.subcategory,
            severity=submission.severity,
            urgency=submission.urgency,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: uuid.UUID):
    """Get a specific submission by ID."""
    from app.infrastructure.database.repositories.submission import SubmissionRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        repo = SubmissionRepository(session)
        submission = await repo.get_by_id(submission_id)

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )

        return SubmissionResponse(
            id=submission.id,
            status=submission.status.value,
            source_modality=submission.source_modality.value,
            original_content=submission.original_content,
            normalized_content=submission.normalized_content,
            detected_language=submission.detected_language,
            category=submission.category,
            subcategory=submission.subcategory,
            severity=submission.severity,
            urgency=submission.urgency,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message to the AI chat assistant."""
    from app.application.workflows.chat import ChatWorkflow

    workflow = ChatWorkflow()

    citizen_id = uuid.uuid4()

    response = await workflow.process_citizen_message(
        citizen_id=citizen_id,
        message=message.content,
        detected_language=message.detected_language,
    )

    return ChatResponse(
        message=ChatMessage(
            role=response["ai_response"]["role"],
            content=response["ai_response"]["content"],
            detected_language=response["ai_response"]["detected_language"],
        ),
        requires_clarification=response["requires_clarification"],
        clarification_questions=response.get("clarification_topics", []),
    )


@router.get("/chat/history/{session_id}", response_model=ConversationHistory)
async def get_chat_history(session_id: uuid.UUID):
    """Get conversation history for a session."""
    return ConversationHistory(
        session_id=session_id,
        messages=[],
        state="active",
        current_round=0,
        max_rounds=3,
        language=None,
    )
