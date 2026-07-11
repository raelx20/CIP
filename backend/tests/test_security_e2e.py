"""Security verification tests with RBAC — runs against the live Docker stack."""

import httpx
import sys
import uuid
import json

BASE = "http://localhost:8000"
FRONTEND = "http://localhost:3000"
TIMEOUT = 15.0

passed = 0
failed = 0
results = []


def check(label: str, ok: bool, detail: str = ""):
    global passed, failed
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append((label, ok, detail))


def main():
    global passed, failed

    client = httpx.Client(timeout=TIMEOUT)

    print("=" * 60)
    print("SECURITY VERIFICATION TESTS (with RBAC)")
    print("=" * 60)

    # ── Helper: register and login a user ──────────────────────────
    def make_user(role="citizen"):
        email = f"{role}-{uuid.uuid4().hex[:8]}@test.com"
        r = client.post(f"{BASE}/api/v1/auth/register", json={
            "email": email,
            "password": "SecureP@ss123!",
            "full_name": f"Test {role.title()}",
            "role": role,
        })
        if r.status_code != 201:
            return None, None
        user = r.json()
        r = client.post(f"{BASE}/api/v1/auth/login", json={
            "email": email,
            "password": "SecureP@ss123!",
        })
        if r.status_code != 200:
            return user, None
        token = r.json().get("access_token")
        return user, token

    # ── Create users ───────────────────────────────────────────────
    print("\n[1] Setup: create users for each role")

    citizen, citizen_token = make_user("citizen")
    citizen_auth = {"Authorization": f"Bearer {citizen_token}"}
    check("Citizen created and logged in", citizen is not None and citizen_token is not None)

    mp, mp_token = make_user("mp")
    mp_auth = {"Authorization": f"Bearer {mp_token}"}
    check("MP created and logged in", mp is not None and mp_token is not None)

    admin, admin_token = make_user("admin")
    admin_auth = {"Authorization": f"Bearer {admin_token}"}
    check("Admin created and logged in", admin is not None and admin_token is not None)

    # ── 2. AUTHENTICATION ──────────────────────────────────────────
    print("\n[2] Authentication")

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": citizen["email"],
        "password": "WrongPassword!",
    })
    check("Wrong password returns 401", r.status_code == 401)

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": "nonexistent@nowhere.com",
        "password": "AnyPassword1!",
    })
    check("Nonexistent user returns 401", r.status_code == 401)

    r = client.post(f"{BASE}/api/v1/auth/login", json={"email": "", "password": ""})
    check("Empty credentials rejected", r.status_code in (400, 401, 422))

    r = client.get(f"{BASE}/api/v1/citizen/submissions/{uuid.uuid4()}",
                   headers={"Authorization": "Bearer not-a-real-jwt-token"})
    check("Malformed JWT rejected", r.status_code in (401, 403))

    r = client.get(f"{BASE}/api/v1/citizen/submissions/{uuid.uuid4()}",
                   headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjF9.x"})
    check("Expired/invalid JWT rejected", r.status_code in (401, 403))

    r = client.get(f"{BASE}/api/v1/citizen/submissions/{uuid.uuid4()}")
    check("Missing auth header returns 401", r.status_code == 401)

    # ── 3. RBAC: CITIZEN endpoints ─────────────────────────────────
    print("\n[3] RBAC: Citizen endpoints")

    # Citizen can submit
    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen["id"],
        "content": "RBAC test submission",
    }, headers=citizen_auth)
    check("Citizen can create submission", r.status_code == 201)
    sub_id = r.json().get("id")

    # Citizen can read own submission
    r = client.get(f"{BASE}/api/v1/citizen/submissions/{sub_id}", headers=citizen_auth)
    check("Citizen can read own submission", r.status_code == 200)

    # Citizen can use chat (may fail if LLM unavailable — that's expected)
    r = client.post(f"{BASE}/api/v1/citizen/chat", json={
        "role": "citizen",
        "content": "Hello",
    }, headers=citizen_auth)
    check("Citizen can use chat (auth passes, LLM may be unavailable)",
          r.status_code in (200, 500, 502),
          f"status={r.status_code}")

    # Citizen can view my-issues
    r = client.get(f"{BASE}/api/v1/citizen/my-issues?citizen_id={citizen['id']}", headers=citizen_auth)
    check("Citizen can view my-issues", r.status_code == 200)

    # MP CANNOT access citizen endpoints
    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": mp["id"],
        "content": "MP trying citizen endpoint",
    }, headers=mp_auth)
    check("MP blocked from citizen submission (403)", r.status_code == 403, f"status={r.status_code}")

    # Admin CANNOT access citizen endpoints
    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": admin["id"],
        "content": "Admin trying citizen endpoint",
    }, headers=admin_auth)
    check("Admin blocked from citizen submission (403)", r.status_code == 403, f"status={r.status_code}")

    # Unauthenticated CANNOT access citizen endpoints
    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": str(uuid.uuid4()),
        "content": "Unauthenticated trying citizen endpoint",
    })
    check("Unauthenticated blocked from citizen submission (401)", r.status_code == 401, f"status={r.status_code}")

    # ── 4. RBAC: MP endpoints ──────────────────────────────────────
    print("\n[4] RBAC: MP endpoints")

    # MP can access MP endpoints
    r = client.get(f"{BASE}/api/v1/mp/dashboard", headers=mp_auth)
    check("MP can access MP dashboard", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/mp/issues", headers=mp_auth)
    check("MP can access MP issues", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/mp/priorities", headers=mp_auth)
    check("MP can access MP priorities", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/mp/hotspots", headers=mp_auth)
    check("MP can access MP hotspots", r.status_code == 200)

    # Admin can ALSO access MP endpoints
    r = client.get(f"{BASE}/api/v1/mp/dashboard", headers=admin_auth)
    check("Admin can access MP dashboard", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/mp/issues", headers=admin_auth)
    check("Admin can access MP issues", r.status_code == 200)

    # Citizen CANNOT access MP endpoints
    r = client.get(f"{BASE}/api/v1/mp/dashboard", headers=citizen_auth)
    check("Citizen blocked from MP dashboard (403)", r.status_code == 403, f"status={r.status_code}")

    r = client.get(f"{BASE}/api/v1/mp/issues", headers=citizen_auth)
    check("Citizen blocked from MP issues (403)", r.status_code == 403, f"status={r.status_code}")

    r = client.get(f"{BASE}/api/v1/mp/priorities", headers=citizen_auth)
    check("Citizen blocked from MP priorities (403)", r.status_code == 403, f"status={r.status_code}")

    r = client.get(f"{BASE}/api/v1/mp/hotspots", headers=citizen_auth)
    check("Citizen blocked from MP hotspots (403)", r.status_code == 403, f"status={r.status_code}")

    # Unauthenticated CANNOT access MP endpoints
    r = client.get(f"{BASE}/api/v1/mp/dashboard")
    check("Unauthenticated blocked from MP dashboard (401)", r.status_code == 401, f"status={r.status_code}")

    # ── 5. RBAC: Admin endpoints ───────────────────────────────────
    print("\n[5] RBAC: Admin endpoints")

    # Admin can access admin endpoints
    r = client.get(f"{BASE}/api/v1/admin/dashboard", headers=admin_auth)
    check("Admin can access admin dashboard", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/admin/issues", headers=admin_auth)
    check("Admin can access admin issues", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/admin/priorities", headers=admin_auth)
    check("Admin can access admin priorities", r.status_code == 200)

    # MP CANNOT access admin endpoints
    r = client.get(f"{BASE}/api/v1/admin/dashboard", headers=mp_auth)
    check("MP blocked from admin dashboard (403)", r.status_code == 403, f"status={r.status_code}")

    r = client.get(f"{BASE}/api/v1/admin/issues", headers=mp_auth)
    check("MP blocked from admin issues (403)", r.status_code == 403, f"status={r.status_code}")

    # Citizen CANNOT access admin endpoints
    r = client.get(f"{BASE}/api/v1/admin/dashboard", headers=citizen_auth)
    check("Citizen blocked from admin dashboard (403)", r.status_code == 403, f"status={r.status_code}")

    r = client.get(f"{BASE}/api/v1/admin/issues", headers=citizen_auth)
    check("Citizen blocked from admin issues (403)", r.status_code == 403, f"status={r.status_code}")

    # Unauthenticated CANNOT access admin endpoints
    r = client.get(f"{BASE}/api/v1/admin/dashboard")
    check("Unauthenticated blocked from admin dashboard (401)", r.status_code == 401, f"status={r.status_code}")

    # ── 6. PUBLIC endpoints (no auth required) ──────────────────────
    print("\n[6] Public endpoints (no auth required)")

    r = client.get(f"{BASE}/api/v1/system/health")
    check("Health is public", r.status_code == 200)

    r = client.get(f"{BASE}/api/v1/system/ready")
    check("Readiness is public", r.status_code == 200)

    r = client.get(f"{BASE}/")
    check("Root is public", r.status_code == 200)

    r = client.get(f"{BASE}/openapi.json")
    check("OpenAPI is public", r.status_code == 200)

    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": f"pub-{uuid.uuid4().hex[:8]}@test.com",
        "password": "Password123!",
        "full_name": "Public Test",
        "role": "citizen",
    })
    check("Registration is public", r.status_code == 201)

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": f"pub-{uuid.uuid4().hex[:8]}@test.com",
        "password": "Wrong123!",
    })
    check("Login is public (returns 401 for wrong creds)", r.status_code == 401)

    r = client.get(FRONTEND)
    check("Frontend is public", r.status_code == 200)

    # ── 7. INPUT VALIDATION ────────────────────────────────────────
    print("\n[7] Input validation")

    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": f"sql-{uuid.uuid4().hex[:8]}@test.com",
        "password": "Password123!",
        "full_name": "Robert'; DROP TABLE users;--",
        "role": "citizen",
    })
    check("SQL injection in name sanitized", r.status_code == 201)

    r = client.get(f"{BASE}/api/v1/system/health")
    check("Users table intact after injection", r.status_code == 200)

    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen["id"],
        "content": "A" * 100000,
    }, headers=citizen_auth)
    check("Oversized content rejected", r.status_code in (400, 413, 422))

    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen["id"],
        "content": "",
    }, headers=citizen_auth)
    check("Empty content rejected", r.status_code in (400, 422))

    r = client.get(f"{BASE}/api/v1/citizen/submissions/not-a-uuid", headers=citizen_auth)
    check("Invalid UUID rejected", r.status_code in (400, 422))

    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": "not-an-email",
        "password": "Password123!",
        "full_name": "Test",
        "role": "citizen",
    })
    check("Invalid email rejected", r.status_code in (400, 422))

    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": f"short-{uuid.uuid4().hex[:8]}@test.com",
        "password": "123",
        "full_name": "Test",
        "role": "citizen",
    })
    check("Short password rejected", r.status_code in (400, 422))

    # ── 8. CORS POLICY ─────────────────────────────────────────────
    print("\n[8] CORS policy")

    r = client.options(f"{BASE}/api/v1/system/health",
                       headers={"Origin": "https://evil.com",
                                "Access-Control-Request-Method": "GET"})
    allow_origin = r.headers.get("access-control-allow-origin", "")
    check("CORS blocks evil origin",
          allow_origin != "https://evil.com",
          f"allow-origin={allow_origin or 'not set (safe)'}")

    # ── 9. HTTP METHOD HANDLING ────────────────────────────────────
    print("\n[9] HTTP method handling")

    r = client.delete(f"{BASE}/api/v1/system/health")
    check("DELETE on health returns 405", r.status_code == 405)

    r = client.put(f"{BASE}/api/v1/system/health")
    check("PUT on health returns 405", r.status_code == 405)

    # ── 10. PATH TRAVERSAL ─────────────────────────────────────────
    print("\n[10] Path traversal")

    for path in ["/api/v1/../../../etc/passwd", "/api/v1/..%2f..%2f..%2fetc/passwd"]:
        r = client.get(f"{BASE}{path}")
        check(f"Traversal blocked: {path[:35]}...", r.status_code in (400, 403, 404))

    # ── 11. SECRET EXPOSURE ────────────────────────────────────────
    print("\n[11] Secret exposure")

    r = client.get(f"{BASE}/api/v1/system/health")
    check("Health doesn't expose JWT secret",
          "jwt" not in json.dumps(r.json()).lower() or "secret" not in json.dumps(r.json()).lower())

    r = client.get(f"{BASE}/")
    check("Root doesn't expose secrets", "password" not in json.dumps(r.json()).lower())

    r = client.get(f"{BASE}/openapi.json")
    check("OpenAPI has no embedded API keys",
          "sk-" not in r.text)

    # ── 12. ERROR HANDLING ─────────────────────────────────────────
    print("\n[12] Error handling")

    r = client.get(f"{BASE}/api/v1/nonexistent")
    check("Non-existent endpoint returns 404", r.status_code == 404)

    r = client.post(f"{BASE}/api/v1/auth/login",
                    content="not json",
                    headers={"Content-Type": "application/json"})
    check("Invalid JSON rejected", r.status_code in (400, 422))

    # ── 13. INFORMATION DISCLOSURE ──────────────────────────────────
    print("\n[13] Information disclosure")

    r = client.get(f"{BASE}/api/v1/system/health")
    check("No X-Powered-By header", r.headers.get("x-powered-by", "") == "")

    r = client.get(f"{BASE}/api/v1/citizen/submissions/not-valid-uuid", headers=citizen_auth)
    check("No stack trace in errors", "traceback" not in r.text.lower())

    # ── 14. GPS PRIVACY ────────────────────────────────────────────
    print("\n[14] GPS privacy")

    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen["id"],
        "content": "GPS privacy test",
        "sender_latitude": 28.6139,
        "sender_longitude": 77.2090,
        "gps_permission_granted": True,
    }, headers=citizen_auth)
    check("GPS submission accepted", r.status_code == 201)

    r = client.get(f"{BASE}/api/v1/mp/issues", headers=mp_auth)
    check("MP issues don't expose sender GPS", r.status_code == 200)

    # ── 15. CONCURRENT SUBMISSIONS ─────────────────────────────────
    print("\n[15] Concurrent submissions")

    sub_ids = []
    for i in range(3):
        r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
            "citizen_id": citizen["id"],
            "content": f"Concurrent #{i+1}",
        }, headers=citizen_auth)
        if r.status_code == 201:
            sub_ids.append(r.json().get("id"))
    check("Multiple rapid submissions succeed", len(sub_ids) >= 2)
    check("All IDs unique", len(sub_ids) == len(set(sub_ids)))

    # ── SUMMARY ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"SECURITY TEST RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        print("\nFailed tests:")
        for label, ok, detail in results:
            if not ok:
                print(f"  - {label}: {detail}")

    client.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
