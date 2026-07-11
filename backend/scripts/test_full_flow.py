"""
Full CIP Citizen Submission Flow Test
Run this after database is connected and vLLM is running.
"""

import asyncio
import uuid
from datetime import datetime, timezone

async def test_full_flow():
    print("=" * 60)
    print("CIP Full Citizen Submission Flow Test")
    print("=" * 60)

    # Step 1: Test Database Connection
    print("\n[1/8] Testing database connection...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from app.config import settings

        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("  ✓ Database connected")
        await engine.dispose()
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print("  Please check your PostgreSQL password and try again.")
        return

    # Step 2: Create Tables
    print("\n[2/8] Creating database tables...")
    try:
        from app.database.base import Base
        from app.database.models import user, submission, location, conversation, assessment, authenticity, issue, evidence, priority, recommendation, review, routing
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.config import settings

        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        print("  ✓ Tables created")
    except Exception as e:
        print(f"  ✗ Table creation failed: {e}")
        return

    # Step 3: Test Intake Workflow
    print("\n[3/8] Testing intake workflow...")
    try:
        from app.application.workflows.intake import IntakeWorkflow

        workflow = IntakeWorkflow()
        citizen_id = uuid.uuid4()

        submission = await workflow.process_text_input(
            citizen_id=citizen_id,
            content="The road near Bhubaneswar Railway Station has many dangerous potholes. Several accidents have happened. About 500 people use this road daily.",
            source_channel="api",
            language="en",
            gps_permission_granted=True,
            sender_latitude=20.2961,
            sender_longitude=85.8245,
        )

        print(f"  ✓ Submission created: {submission['id']}")
        print(f"    Status: {submission['status']}")
    except Exception as e:
        print(f"  ✗ Intake workflow failed: {e}")
        return

    # Step 4: Test Assessment Workflow
    print("\n[4/8] Testing assessment workflow...")
    try:
        from app.application.workflows.assess_submission import AssessSubmissionWorkflow

        workflow = AssessSubmissionWorkflow()
        assessment = await workflow.assess(
            submission_id=submission['id'],
            original_content=submission['original_content'],
            detected_language="en",
        )

        print(f"  ✓ Assessment created: {assessment['assessment']['id']}")
        print(f"    Category: {assessment['assessment']['category']}")
    except Exception as e:
        print(f"  ✗ Assessment workflow failed: {e}")
        return

    # Step 5: Test Priority Engine
    print("\n[5/8] Testing priority engine...")
    try:
        from app.domain.priority_engine import PriorityEngine
        from app.domain.priority.value_objects import ThreatDimension

        engine = PriorityEngine()
        dimension_scores = {dim.value: 0.6 for dim in ThreatDimension}
        dimension_scores[ThreatDimension.PUBLIC_CRITICISM_RISK.value] = 0.8
        dimension_scores[ThreatDimension.HUMANITARIAN_CONCERN.value] = 0.7

        priority = engine.calculate_priority(
            dimension_scores=dimension_scores,
            submission_count=15,
            urgency=7,
            severity=6,
        )

        print(f"  ✓ Priority calculated: {priority.final_score:.3f} ({priority.priority_level.value})")
        print(f"    Top 3 dimensions:")
        top_dims = sorted(priority.components, key=lambda c: c.weighted_score, reverse=True)[:3]
        for comp in top_dims:
            print(f"      - {comp.dimension.value}: {comp.normalized_value:.2f}")
    except Exception as e:
        print(f"  ✗ Priority engine failed: {e}")
        return

    # Step 6: Test Authenticity Engine
    print("\n[6/8] Testing authenticity engine...")
    try:
        from app.domain.authenticity_engine import AuthenticityEngine
        from app.domain.authenticity.value_objects import SignalType

        engine = AuthenticityEngine()
        signals = {
            SignalType.GEOGRAPHIC_CONSISTENCY: 0.8,
            SignalType.LOCATION_VALIDITY: 0.9,
            SignalType.CLARIFICATION_CONSISTENCY: 0.7,
            SignalType.INTERNAL_CONTRADICTION: 0.9,
        }

        authenticity = engine.assess_authenticity(
            signals=signals,
            gps_permission_granted=True,
        )

        print(f"  ✓ Authenticity assessed: {authenticity.score:.3f} ({authenticity.status.value})")
        print(f"    Confidence: {authenticity.confidence:.3f}")
        print(f"    Review required: {authenticity.review_required}")
    except Exception as e:
        print(f"  ✗ Authenticity engine failed: {e}")
        return

    # Step 7: Test Department Router
    print("\n[7/8] Testing department router...")
    try:
        from app.domain.department_router import DepartmentRouter

        router = DepartmentRouter()
        routing = router.route(
            category="road",
            subcategory="potholes",
            location_context={"city": "Bhubaneswar"},
        )

        print(f"  ✓ Department routed: {routing['primary_department']}")
        print(f"    Confidence: {routing['confidence']:.2f}")
        print(f"    Alternatives: {routing['alternative_departments']}")
    except Exception as e:
        print(f"  ✗ Department router failed: {e}")
        return

    # Step 8: Test Chat Workflow
    print("\n[8/8] Testing chat workflow...")
    try:
        from app.application.workflows.chat import ChatWorkflow

        workflow = ChatWorkflow()
        response = await workflow.process_citizen_message(
            citizen_id=uuid.uuid4(),
            message="I want to report a water problem in my area",
            detected_language="en",
        )

        print(f"  ✓ Chat response generated")
        print(f"    AI: {response['ai_response']['content'][:80]}...")
        print(f"    Requires clarification: {response['requires_clarification']}")
    except Exception as e:
        print(f"  ✗ Chat workflow failed: {e}")
        return

    # Summary
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nCIP Backend is ready for testing.")
    print("\nNext steps:")
    print("  1. Start the server: uvicorn app.main:app --reload")
    print("  2. Open API docs: http://localhost:8000/docs")
    print("  3. Test citizen submission: POST /api/v1/citizen/submissions")
    print("  4. Test admin dashboard: GET /api/v1/admin/dashboard")


if __name__ == "__main__":
    asyncio.run(test_full_flow())
