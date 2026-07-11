from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert "service" in body
        assert "version" in body

    def test_health_has_required_fields(self):
        response = client.get("/api/v1/system/health")
        body = response.json()
        required_fields = ["status", "service", "version", "environment"]
        for field in required_fields:
            assert field in body, f"Missing field: {field}"


class TestReadiness:
    def test_readiness_returns_structure(self):
        response = client.get("/api/v1/system/ready")
        assert response.status_code in (200, 503)
        body = response.json()
        assert "status" in body
        assert body["status"] in ("ready", "not_ready")
