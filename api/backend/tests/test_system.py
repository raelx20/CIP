from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["service"] == "Constituency Intelligence Platform"
    assert body["version"] == "1.0.0"
    assert body["environment"] == "development"
    assert body["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert body["service"] == "Constituency Intelligence Platform"
    assert body["version"] == "1.0.0"


def test_generated_request_id():
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) > 0


def test_provided_request_id_is_preserved():
    request_id = "cip-test-request-001"

    response = client.get(
        "/api/v1/system/health",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id