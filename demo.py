"""Quick local demo for the Habit Tracker API.

Run:
    python demo.py
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


def run_demo() -> None:
    client = TestClient(app)

    email = f"demo_{uuid4().hex[:8]}@example.com"
    password = "demo123456"

    print("=== 1) Register ===")
    register_resp = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    print(register_resp.status_code, register_resp.json())

    print("\n=== 2) Login ===")
    login_resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    print(login_resp.status_code, login_resp.json())
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n=== 3) Create Habit ===")
    create_habit_resp = client.post(
        "/habits",
        json={"name": "每天跑步", "description": "至少 20 分钟"},
        headers=headers,
    )
    print(create_habit_resp.status_code, create_habit_resp.json())
    habit_id = create_habit_resp.json()["id"]

    print("\n=== 4) Check-in (today) ===")
    checkin_resp = client.post(f"/habits/{habit_id}/checkin", json={}, headers=headers)
    print(checkin_resp.status_code, checkin_resp.json())

    print("\n=== 5) Habit Stats ===")
    stats_resp = client.get(f"/habits/{habit_id}/stats", headers=headers)
    print(stats_resp.status_code, stats_resp.json())

    print("\n=== 6) Habit List ===")
    list_resp = client.get("/habits", headers=headers)
    print(list_resp.status_code, list_resp.json())

    print("\nDemo finished on", date.today().isoformat())


if __name__ == "__main__":
    run_demo()
