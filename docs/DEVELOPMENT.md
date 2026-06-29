# Development Guide

## Principles

1. **Design → Implement → Test** — never skip design or testing
2. **Incremental delivery** — one step at a time, no big-bang commits
3. **No hardcoding** — use config, env vars, and database
4. **SOLID & Clean Architecture** — dependencies point inward

## Backend Layout (`backend/app/`)

| Folder | Purpose |
|--------|---------|
| `core/` | Config, database connection, security |
| `domain/` | Entities, repository interfaces, business rules |
| `api/` | FastAPI routers and request/response handling |
| `schemas/` | Pydantic DTOs for API validation |
| `agents/` | LangGraph graphs and individual agents |
| `services/` | Application services orchestrating domain + agents |

## Frontend Layout (`frontend/src/`)

| Folder | Purpose |
|--------|---------|
| `components/` | Reusable UI components |
| `pages/` | Route-level screens |
| `hooks/` | Custom React hooks |
| `services/` | API client layer |
| `stores/` | Global state (auth, theme, user) |
| `types/` | TypeScript interfaces |
| `utils/` | Helpers |

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in values before running the backend (Step 3).

## Local Development (after Steps 3–4)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
