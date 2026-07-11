"""Unit tests for role-based access control (RBAC) dependencies and endpoint enforcement."""

import pytest
from unittest.mock import patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user,
    require_role,
    require_citizen,
    require_mp,
    require_admin,
    require_officer,
)
from app.security.authentication import create_access_token


# ── Test app with RBAC-protected endpoints ─────────────────────────

app = FastAPI()


@app.get("/public")
async def public_endpoint():
    return {"status": "ok"}


@app.get("/citizen-only", dependencies=[Depends(require_citizen)])
async def citizen_only():
    return {"role": "citizen"}


@app.get("/mp-only", dependencies=[Depends(require_mp)])
async def mp_only():
    return {"role": "mp"}


@app.get("/admin-only", dependencies=[Depends(require_admin)])
async def admin_only():
    return {"role": "admin"}


@app.get("/officer-only", dependencies=[Depends(require_officer)])
async def officer_only():
    return {"role": "officer"}


@app.get("/custom-role", dependencies=[Depends(require_role("citizen", "officer"))])
async def custom_role():
    return {"role": "custom"}


@app.get("/auth-user", dependencies=[Depends(get_current_user)])
async def auth_user(current_user: dict = Depends(get_current_user)):
    return {"role": current_user.get("role")}


client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────

def make_token(role: str, sub: str = "test-user") -> str:
    return create_access_token({"sub": sub, "role": role})


def auth_header(role: str) -> dict:
    return {"Authorization": f"Bearer {make_token(role)}"}


# ── Tests: get_current_user ────────────────────────────────────────

class TestGetCurrentUser:
    def test_valid_token(self):
        r = client.get("/auth-user", headers=auth_header("citizen"))
        assert r.status_code == 200
        assert r.json()["role"] == "citizen"

    def test_missing_header(self):
        r = client.get("/auth-user")
        assert r.status_code == 401

    def test_malformed_header_no_bearer(self):
        r = client.get("/auth-user", headers={"Authorization": "Token abc"})
        assert r.status_code == 401

    def test_malformed_header_bearer_only(self):
        r = client.get("/auth-user", headers={"Authorization": "Bearer "})
        assert r.status_code == 401

    def test_invalid_jwt_token(self):
        r = client.get("/auth-user", headers={"Authorization": "Bearer not-a-jwt"})
        assert r.status_code == 401

    def test_expired_jwt_token(self):
        from datetime import timedelta
        token = create_access_token(
            {"sub": "user", "role": "citizen"},
            expires_delta=timedelta(seconds=-1),
        )
        r = client.get("/auth-user", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_empty_header_value(self):
        r = client.get("/auth-user", headers={"Authorization": ""})
        assert r.status_code == 401


# ── Tests: require_role factory ────────────────────────────────────

class TestRequireRole:
    def test_single_role_allowed(self):
        r = client.get("/citizen-only", headers=auth_header("citizen"))
        assert r.status_code == 200

    def test_single_role_wrong(self):
        r = client.get("/citizen-only", headers=auth_header("mp"))
        assert r.status_code == 403

    def test_multiple_roles_first_allowed(self):
        r = client.get("/mp-only", headers=auth_header("mp"))
        assert r.status_code == 200

    def test_multiple_roles_second_allowed(self):
        r = client.get("/mp-only", headers=auth_header("admin"))
        assert r.status_code == 200

    def test_multiple_roles_none_allowed(self):
        r = client.get("/mp-only", headers=auth_header("citizen"))
        assert r.status_code == 403

    def test_custom_role_combination(self):
        # "citizen" and "officer" allowed
        r = client.get("/custom-role", headers=auth_header("citizen"))
        assert r.status_code == 200

        r = client.get("/custom-role", headers=auth_header("officer"))
        assert r.status_code == 200

        r = client.get("/custom-role", headers=auth_header("mp"))
        assert r.status_code == 403

        r = client.get("/custom-role", headers=auth_header("admin"))
        assert r.status_code == 403

    def test_unauthenticated_returns_401_not_403(self):
        r = client.get("/citizen-only")
        assert r.status_code == 401

    def test_wrong_role_returns_403_not_401(self):
        r = client.get("/citizen-only", headers=auth_header("admin"))
        assert r.status_code == 403


# ── Tests: pre-built role dependencies ─────────────────────────────

class TestRequireCitizen:
    def test_citizen_allowed(self):
        r = client.get("/citizen-only", headers=auth_header("citizen"))
        assert r.status_code == 200

    def test_mp_blocked(self):
        r = client.get("/citizen-only", headers=auth_header("mp"))
        assert r.status_code == 403

    def test_admin_blocked(self):
        r = client.get("/citizen-only", headers=auth_header("admin"))
        assert r.status_code == 403

    def test_officer_blocked(self):
        r = client.get("/citizen-only", headers=auth_header("officer"))
        assert r.status_code == 403


class TestRequireMp:
    def test_mp_allowed(self):
        r = client.get("/mp-only", headers=auth_header("mp"))
        assert r.status_code == 200

    def test_admin_allowed(self):
        r = client.get("/mp-only", headers=auth_header("admin"))
        assert r.status_code == 200

    def test_citizen_blocked(self):
        r = client.get("/mp-only", headers=auth_header("citizen"))
        assert r.status_code == 403

    def test_officer_blocked(self):
        r = client.get("/mp-only", headers=auth_header("officer"))
        assert r.status_code == 403


class TestRequireAdmin:
    def test_admin_allowed(self):
        r = client.get("/admin-only", headers=auth_header("admin"))
        assert r.status_code == 200

    def test_mp_blocked(self):
        r = client.get("/admin-only", headers=auth_header("mp"))
        assert r.status_code == 403

    def test_citizen_blocked(self):
        r = client.get("/admin-only", headers=auth_header("citizen"))
        assert r.status_code == 403

    def test_officer_blocked(self):
        r = client.get("/admin-only", headers=auth_header("officer"))
        assert r.status_code == 403


class TestRequireOfficer:
    def test_officer_allowed(self):
        r = client.get("/officer-only", headers=auth_header("officer"))
        assert r.status_code == 200

    def test_admin_allowed(self):
        r = client.get("/officer-only", headers=auth_header("admin"))
        assert r.status_code == 200

    def test_citizen_blocked(self):
        r = client.get("/officer-only", headers=auth_header("citizen"))
        assert r.status_code == 403

    def test_mp_blocked(self):
        r = client.get("/officer-only", headers=auth_header("mp"))
        assert r.status_code == 403


# ── Tests: public endpoints (no auth) ──────────────────────────────

class TestPublicEndpoints:
    def test_public_no_token(self):
        r = client.get("/public")
        assert r.status_code == 200

    def test_public_with_token(self):
        r = client.get("/public", headers=auth_header("citizen"))
        assert r.status_code == 200


# ── Tests: error response format ───────────────────────────────────

class TestErrorFormat:
    def test_401_has_detail(self):
        r = client.get("/citizen-only")
        assert r.status_code == 401
        body = r.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)

    def test_403_has_detail(self):
        r = client.get("/citizen-only", headers=auth_header("admin"))
        assert r.status_code == 403
        body = r.json()
        assert "detail" in body
        assert "Required role" in body["detail"]

    def test_401_no_body_leak(self):
        r = client.get("/auth-user")
        assert r.status_code == 401
        body = r.json()
        # Should not expose internal implementation details
        assert "traceback" not in str(body).lower()
        assert "secret" not in str(body).lower()


# ── Tests: actual FastAPI app routes (integration with real router) ─

from app.main import app as real_app

real_client = TestClient(real_app)


class TestRealAppRBAC:
    """Tests RBAC enforcement on the actual CIP FastAPI app routes.

    Only tests auth/rejection behavior (401/403) which doesn't require DB access.
    Tests that pass auth may hit DB errors (FK, connection) — that's expected
    and not an RBAC concern.
    """

    def _citizen_auth(self):
        return auth_header("citizen")

    def _mp_auth(self):
        return auth_header("mp")

    def _admin_auth(self):
        return auth_header("admin")

    # ── Citizen endpoints: unauthenticated & wrong-role ──

    def test_citizen_submission_requires_auth(self):
        r = real_client.post("/api/v1/citizen/submissions", json={
            "citizen_id": "00000000-0000-0000-0000-000000000001",
            "content": "test",
        })
        assert r.status_code == 401

    def test_citizen_submission_mp_blocked(self):
        r = real_client.post("/api/v1/citizen/submissions", json={
            "citizen_id": "00000000-0000-0000-0000-000000000001",
            "content": "test",
        }, headers=self._mp_auth())
        assert r.status_code == 403

    def test_citizen_submission_admin_blocked(self):
        r = real_client.post("/api/v1/citizen/submissions", json={
            "citizen_id": "00000000-0000-0000-0000-000000000001",
            "content": "test",
        }, headers=self._admin_auth())
        assert r.status_code == 403

    def test_citizen_chat_requires_auth(self):
        r = real_client.post("/api/v1/citizen/chat", json={
            "role": "citizen",
            "content": "hello",
        })
        assert r.status_code == 401

    def test_citizen_chat_mp_blocked(self):
        r = real_client.post("/api/v1/citizen/chat", json={
            "role": "citizen",
            "content": "hello",
        }, headers=self._mp_auth())
        assert r.status_code == 403

    def test_citizen_my_issues_requires_auth(self):
        r = real_client.get("/api/v1/citizen/my-issues?citizen_id=00000000-0000-0000-0000-000000000001")
        assert r.status_code == 401

    def test_citizen_my_issues_mp_blocked(self):
        r = real_client.get(
            "/api/v1/citizen/my-issues?citizen_id=00000000-0000-0000-0000-000000000001",
            headers=self._mp_auth(),
        )
        assert r.status_code == 403

    # ── MP endpoints ──

    def test_mp_dashboard_requires_auth(self):
        r = real_client.get("/api/v1/mp/dashboard")
        assert r.status_code == 401

    def test_mp_dashboard_citizen_blocked(self):
        r = real_client.get("/api/v1/mp/dashboard", headers=self._citizen_auth())
        assert r.status_code == 403

    def test_mp_issues_requires_auth(self):
        r = real_client.get("/api/v1/mp/issues")
        assert r.status_code == 401

    def test_mp_issues_citizen_blocked(self):
        r = real_client.get("/api/v1/mp/issues", headers=self._citizen_auth())
        assert r.status_code == 403

    def test_mp_priorities_requires_auth(self):
        r = real_client.get("/api/v1/mp/priorities")
        assert r.status_code == 401

    def test_mp_priorities_citizen_blocked(self):
        r = real_client.get("/api/v1/mp/priorities", headers=self._citizen_auth())
        assert r.status_code == 403

    def test_mp_hotspots_requires_auth(self):
        r = real_client.get("/api/v1/mp/hotspots")
        assert r.status_code == 401

    def test_mp_hotspots_citizen_blocked(self):
        r = real_client.get("/api/v1/mp/hotspots", headers=self._citizen_auth())
        assert r.status_code == 403

    # ── Admin endpoints ──

    def test_admin_dashboard_requires_auth(self):
        r = real_client.get("/api/v1/admin/dashboard")
        assert r.status_code == 401

    def test_admin_dashboard_mp_blocked(self):
        r = real_client.get("/api/v1/admin/dashboard", headers=self._mp_auth())
        assert r.status_code == 403

    def test_admin_dashboard_citizen_blocked(self):
        r = real_client.get("/api/v1/admin/dashboard", headers=self._citizen_auth())
        assert r.status_code == 403

    def test_admin_issues_requires_auth(self):
        r = real_client.get("/api/v1/admin/issues")
        assert r.status_code == 401

    def test_admin_issues_mp_blocked(self):
        r = real_client.get("/api/v1/admin/issues", headers=self._mp_auth())
        assert r.status_code == 403

    def test_admin_priorities_requires_auth(self):
        r = real_client.get("/api/v1/admin/priorities")
        assert r.status_code == 401

    def test_admin_priorities_citizen_blocked(self):
        r = real_client.get("/api/v1/admin/priorities", headers=self._citizen_auth())
        assert r.status_code == 403

    # ── Public endpoints (no auth required) ──

    def test_health_is_public(self):
        r = real_client.get("/api/v1/system/health")
        assert r.status_code == 200

    def test_readiness_is_public(self):
        r = real_client.get("/api/v1/system/ready")
        # 200 if DB available, 503 if DB unavailable — both are valid public responses
        assert r.status_code in (200, 503)

    def test_root_is_public(self):
        r = real_client.get("/")
        assert r.status_code == 200

    # ── Cross-role blocking matrix (no DB needed) ──

    def test_full_cross_role_matrix(self):
        """Verify the complete RBAC matrix for all blocked combinations.

        Only tests 401/403 responses which don't touch the DB.
        """
        roles = {
            "citizen": self._citizen_auth(),
            "mp": self._mp_auth(),
            "admin": self._admin_auth(),
        }

        blocked_combos = [
            ("/api/v1/citizen/my-issues?citizen_id=00000000-0000-0000-0000-000000000001", "mp"),
            ("/api/v1/citizen/my-issues?citizen_id=00000000-0000-0000-0000-000000000001", "admin"),
            ("/api/v1/mp/dashboard", "citizen"),
            ("/api/v1/mp/issues", "citizen"),
            ("/api/v1/mp/priorities", "citizen"),
            ("/api/v1/mp/hotspots", "citizen"),
            ("/api/v1/admin/dashboard", "citizen"),
            ("/api/v1/admin/dashboard", "mp"),
            ("/api/v1/admin/issues", "citizen"),
            ("/api/v1/admin/issues", "mp"),
            ("/api/v1/admin/priorities", "citizen"),
            ("/api/v1/admin/priorities", "mp"),
        ]

        for endpoint, role in blocked_combos:
            r = real_client.get(endpoint, headers=roles[role])
            assert r.status_code == 403, (
                f"{role} should be blocked from {endpoint}, got {r.status_code}"
            )
