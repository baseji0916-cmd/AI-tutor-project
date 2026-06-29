"""Quick live OpenAI + goal pipeline check (uses backend/.env)."""

import sys
from datetime import date, timedelta
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.database.initializer import init_db
from app.main import app
from app.services.openai_service import OpenAIService

get_settings.cache_clear()
init_db()

settings = get_settings()
print("has_key:", settings.has_openai_api_key)
print("model:", settings.openai_model)

svc = OpenAIService()
health = svc.health_check()
print("health:", health.get("status"), health.get("reply"))

client = TestClient(app)
email = f"live{date.today().strftime('%H%M%S')}@test.com"
client.post(
    "/api/v1/auth/register",
    json={"email": email, "username": f"live{date.today().strftime('%H%M%S')}", "password": "securepass123"},
)
token = client.post("/api/v1/auth/login", json={"email": email, "password": "securepass123"}).json()[
    "access_token"
]
headers = {"Authorization": f"Bearer {token}"}
today = date.today()
goal = client.post(
    "/api/v1/goals",
    json={
        "title": "매일 영어 30분",
        "priority": 3,
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=30)).isoformat(),
    },
    headers=headers,
)
print("goal_create:", goal.status_code)
gid = goal.json()["id"]

analyze = client.post(f"/api/ai/goal/{gid}/analyze", headers=headers)
print("analyze:", analyze.status_code, "llm_mode:", analyze.json().get("llm_mode"))

plan = client.post(f"/api/ai/planner/{gid}/generate", headers=headers)
body = plan.json()
print("plan:", plan.status_code, "llm_mode:", body.get("llm_mode"), "missions:", len(body.get("missions", [])))

if body.get("llm_mode") != "openai":
    sys.exit(1)
print("PASS live OpenAI pipeline")
