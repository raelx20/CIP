import asyncio
import uuid
from app.application.workflows.consolidate_issue import ConsolidateIssueWorkflow


async def test_consolidation():
    workflow = ConsolidateIssueWorkflow()

    submission1_id = uuid.uuid4()
    submission2_id = uuid.uuid4()

    result1 = await workflow.consolidate(
        submission_id=submission1_id,
        category="road",
        subcategory="potholes",
        latitude=20.2961,
        longitude=85.8245,
        existing_clusters=[],
    )
    print(f"First submission action: {result1['action']}")
    print(f"Cluster ID: {result1['cluster']['id']}")

    existing_clusters = [{
        "id": result1["cluster"]["id"],
        "category": "road",
        "subcategory": "potholes",
        "latitude": 20.2961,
        "longitude": 85.8245,
    }]

    result2 = await workflow.consolidate(
        submission_id=submission2_id,
        category="road",
        subcategory="potholes",
        latitude=20.2965,
        longitude=85.8250,
        existing_clusters=existing_clusters,
    )
    print(f"Second submission action: {result2['action']}")
    if "cluster_update" in result2:
        print(f"Cluster updated: {result2['cluster_update']}")


if __name__ == "__main__":
    asyncio.run(test_consolidation())
