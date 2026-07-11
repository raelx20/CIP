"""Golden-path E2E test — runs against the live Docker stack."""

import httpx
import sys
import uuid

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
    citizen_token = None
    mp_token = None
    citizen_id = None
    mp_id = None
    submission_id = None

    print("=" * 60)
    print("GOLDEN-PATH E2E TEST")
    print("=" * 60)

    # ── Step 0: Infrastructure health ──────────────────────────────
    print("\n[0] Infrastructure health")

    r = client.get(f"{BASE}/api/v1/system/health")
    check("Backend health returns 200", r.status_code == 200, f"status={r.status_code}")
    body = r.json()
    check("Health status is healthy", body.get("status") == "healthy")
    check("Health has uptime", "uptime_seconds" in body)

    r = client.get(f"{BASE}/api/v1/system/ready")
    check("Backend readiness returns 200", r.status_code == 200)
    body = r.json()
    check("Database connected", body.get("database") == "connected")
    check("Redis connected", body.get("redis") == "connected")

    r = client.get(FRONTEND)
    check("Frontend serves 200", r.status_code == 200)

    r = client.get(f"{BASE}/")
    check("Root endpoint returns service info", r.status_code == 200)

    # ── Step 1: Citizen registration ───────────────────────────────
    print("\n[1] Citizen registration")

    citizen_email = f"citizen-{uuid.uuid4().hex[:8]}@test.com"
    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": citizen_email,
        "password": "TestPass123!",
        "full_name": "Test Citizen",
        "role": "citizen",
    })
    check("Citizen registration returns 201", r.status_code == 201, f"status={r.status_code}")
    citizen_user = r.json()
    citizen_id = citizen_user.get("id")
    check("Citizen has UUID", citizen_id is not None)
    check("Citizen role is citizen", citizen_user.get("role") == "citizen")

    # ── Step 2: Citizen login ──────────────────────────────────────
    print("\n[2] Citizen login")

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": citizen_email,
        "password": "TestPass123!",
    })
    check("Citizen login returns 200", r.status_code == 200, f"status={r.status_code}")
    login_data = r.json()
    citizen_token = login_data.get("access_token")
    check("Login returns access_token", citizen_token is not None)
    check("Login returns user object", login_data.get("user") is not None)
    check("Logged-in user has correct email", login_data["user"].get("email") == citizen_email)

    auth_headers = {"Authorization": f"Bearer {citizen_token}"}

    # ── Step 3: Citizen submits complaint ──────────────────────────
    print("\n[3] Citizen submits complaint")

    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen_id,
        "content": "There is no water supply in our area for the past 3 days. Multiple households are affected.",
        "source_modality": "text",
        "source_channel": "api",
        "language": "en",
        "gps_permission_granted": True,
        "sender_latitude": 28.6139,
        "sender_longitude": 77.2090,
        "sender_gps_accuracy": 10.0,
    }, headers=auth_headers)
    check("Submission created (201)", r.status_code == 201, f"status={r.status_code}")
    sub = r.json()
    submission_id = sub.get("id")
    check("Submission has UUID", submission_id is not None)
    check("Submission has status", sub.get("status") is not None)
    check("Submission has content", sub.get("original_content") is not None)
    check("Submission content preserved", "water supply" in sub.get("original_content", "").lower())

    # ── Step 4: Citizen retrieves submission ───────────────────────
    print("\n[4] Citizen retrieves submission")

    r = client.get(f"{BASE}/api/v1/citizen/submissions/{submission_id}", headers=auth_headers)
    check("Get submission returns 200", r.status_code == 200)
    retrieved = r.json()
    check("Retrieved submission matches", retrieved.get("id") == submission_id)

    # ── Step 5: Citizen checks submission status ───────────────────
    print("\n[5] Citizen checks submission status")

    r = client.get(f"{BASE}/api/v1/citizen/submissions/{submission_id}/status", headers=auth_headers)
    check("Status endpoint returns 200", r.status_code == 200)
    status_data = r.json()
    check("Status has progress field", "progress" in status_data)
    check("Status has status_message", "status_message" in status_data)
    check("Progress is a number", isinstance(status_data.get("progress"), (int, float)))

    # ── Step 6: Citizen checks my-issues ───────────────────────────
    print("\n[6] Citizen checks my-issues")

    r = client.get(f"{BASE}/api/v1/citizen/my-issues?citizen_id={citizen_id}", headers=auth_headers)
    check("My issues returns 200", r.status_code == 200)
    issues_data = r.json()
    check("My issues has issues list", "issues" in issues_data)
    check("My issues has total", "total" in issues_data)

    # ── Step 7: MP registration & login ────────────────────────────
    print("\n[7] MP registration & login")

    mp_email = f"mp-{uuid.uuid4().hex[:8]}@test.com"
    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": mp_email,
        "password": "TestPass123!",
        "full_name": "Test MP",
        "role": "mp",
    })
    check("MP registration returns 201", r.status_code == 201, f"status={r.status_code}")
    mp_user = r.json()
    mp_id = mp_user.get("id")

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": mp_email,
        "password": "TestPass123!",
    })
    check("MP login returns 200", r.status_code == 200)
    mp_token = r.json().get("access_token")
    mp_auth = {"Authorization": f"Bearer {mp_token}"}

    # ── Step 8: MP views dashboard ─────────────────────────────────
    print("\n[8] MP views dashboard")

    r = client.get(f"{BASE}/api/v1/mp/dashboard", headers=mp_auth)
    check("MP dashboard returns 200", r.status_code == 200)
    dash = r.json()
    check("Dashboard has total_submissions", "total_submissions" in dash)
    check("Dashboard has pending_review", "pending_review" in dash)
    check("Dashboard has active_clusters", "active_clusters" in dash)
    check("Total submissions >= 1", dash.get("total_submissions", 0) >= 1,
          f"count={dash.get('total_submissions')}")

    # ── Step 9: MP views issues ────────────────────────────────────
    print("\n[9] MP views issues")

    r = client.get(f"{BASE}/api/v1/mp/issues", headers=mp_auth)
    check("MP issues returns 200", r.status_code == 200)
    issues = r.json()
    check("Issues response has issues list", "issues" in issues)
    check("Issues response has total", "total" in issues)

    # ── Step 10: MP views priorities ───────────────────────────────
    print("\n[10] MP views priorities")

    r = client.get(f"{BASE}/api/v1/mp/priorities", headers=mp_auth)
    check("MP priorities returns 200", r.status_code == 200)
    priorities = r.json()
    check("Priorities has rankings list", "rankings" in priorities)
    check("Priorities has scoring_version", "scoring_version" in priorities)

    # ── Step 11: MP views hotspots ─────────────────────────────────
    print("\n[11] MP views hotspots")

    r = client.get(f"{BASE}/api/v1/mp/hotspots", headers=mp_auth)
    check("MP hotspots returns 200", r.status_code == 200)
    hotspots = r.json()
    check("Hotspots has hotspots list", "hotspots" in hotspots)

    # ── Step 12: Admin registration & login ────────────────────────
    print("\n[12] Admin registration & login")

    admin_email = f"admin-{uuid.uuid4().hex[:8]}@test.com"
    r = client.post(f"{BASE}/api/v1/auth/register", json={
        "email": admin_email,
        "password": "TestPass123!",
        "full_name": "Test Admin",
        "role": "admin",
    })
    check("Admin registration returns 201", r.status_code == 201)

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": admin_email,
        "password": "TestPass123!",
    })
    check("Admin login returns 200", r.status_code == 200)
    admin_token = r.json().get("access_token")
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # ── Step 13: Admin views dashboard ─────────────────────────────
    print("\n[13] Admin views dashboard")

    r = client.get(f"{BASE}/api/v1/admin/dashboard", headers=admin_auth)
    check("Admin dashboard returns 200", r.status_code == 200)

    # ── Step 14: Admin views issues ────────────────────────────────
    print("\n[14] Admin views issues")

    r = client.get(f"{BASE}/api/v1/admin/issues", headers=admin_auth)
    check("Admin issues returns 200", r.status_code == 200)

    # ── Step 15: Admin views priorities ────────────────────────────
    print("\n[15] Admin views priorities")

    r = client.get(f"{BASE}/api/v1/admin/priorities", headers=admin_auth)
    check("Admin priorities returns 200", r.status_code == 200)

    # ── Step 16: Login invalid credentials ─────────────────────────
    print("\n[16] Security: invalid credentials rejected")

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": citizen_email,
        "password": "WrongPassword123!",
    })
    check("Invalid password rejected (401)", r.status_code == 401, f"status={r.status_code}")

    r = client.post(f"{BASE}/api/v1/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "TestPass123!",
    })
    check("Nonexistent user rejected (401)", r.status_code == 401, f"status={r.status_code}")

    # ── Step 17: Duplicate submission ──────────────────────────────
    print("\n[17] Duplicate submission accepted (separate complaint)")

    r = client.post(f"{BASE}/api/v1/citizen/submissions", json={
        "citizen_id": citizen_id,
        "content": "Water supply issue again in the same area. Very urgent.",
        "source_modality": "text",
        "source_channel": "api",
    }, headers=auth_headers)
    check("Second submission created", r.status_code == 201)
    sub2_id = r.json().get("id")
    check("Second submission has different ID", sub2_id != submission_id)

    # ── Step 18: OpenAPI schema ────────────────────────────────────
    print("\n[18] OpenAPI schema")

    r = client.get(f"{BASE}/openapi.json")
    check("OpenAPI schema returns 200", r.status_code == 200)
    spec = r.json()
    check("OpenAPI has paths", len(spec.get("paths", {})) > 0,
          f"count={len(spec.get('paths', {}))}")
    check("OpenAPI has components", "components" in spec)

    # ── Step 19: Frontend pages accessible ─────────────────────────
    print("\n[19] Frontend pages")

    for path in ["/", "/login", "/register"]:
        r = client.get(f"{FRONTEND}{path}")
        check(f"GET {path} returns 200", r.status_code == 200, f"status={r.status_code}")

    # ── Summary ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
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
