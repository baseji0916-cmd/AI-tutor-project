# GrowthPilot (AI-tutor-project)

**AI Growth Coach** — LangGraph Multi-Agent 기반 목표 분석, 계획 생성, 실행 관리, 성장 예측 서비스

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Tailwind CSS 4, PWA |
| Backend | Python, FastAPI, SQLAlchemy 2, Alembic |
| AI | OpenAI API, LangGraph |
| Database | SQLite |
| Deploy | [Vercel](https://vercel.com) (frontend) + [Render](https://render.com) (API) — see [docs/DEPLOY_VERCEL_RENDER.md](docs/DEPLOY_VERCEL_RENDER.md) |

---

## Final Project Structure

```
growthpilot/
├── render.yaml                 # Render Blueprint (API + Web)
├── .env.example                # Root env template
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT.md
│
├── backend/
│   ├── alembic/                # DB migrations
│   ├── scripts/
│   │   ├── start.sh            # Render production startup
│   │   └── verify_deploy.py    # Local verification
│   ├── requirements.txt      # production (Render installs this)
│   ├── requirements-dev.txt    # pytest (local/CI only)
│   └── app/
│       ├── main.py             # FastAPI entry
│       ├── config/             # Settings (dotenv)
│       ├── database/           # Engine, init_db
│       ├── models/             # SQLAlchemy ORM (STEP 2)
│       ├── repositories/       # Repository pattern
│       ├── schemas/            # Pydantic API schemas
│       ├── services/             # Business logic
│       │   └── ai/             # Agent registry
│       ├── routers/            # /auth, /goal, /api/ai, /api/health/ai
│       ├── api/routes/         # /api/v1/* legacy routes
│       ├── agents/             # LangGraph multi-agent (STEP 4)
│       │   ├── graph/
│       │   ├── goal_agent/
│       │   ├── planner_agent/
│       │   ├── memory_agent/
│       │   ├── reflection_agent/
│       │   ├── replanner_agent/
│       │   ├── growth_predictor_agent/
│       │   └── ...
│       ├── core/               # Security, DB re-export
│       └── infrastructure/     # Legacy model re-exports
│
└── frontend/
    ├── src/
    │   ├── pages/              # 12 screens (STEP 5)
    │   ├── components/         # UI + layout
    │   ├── services/           # API clients
    │   ├── hooks/              # useGoals, useTheme
    │   ├── stores/             # AuthContext
    │   └── config/             # Navigation
    ├── vite.config.ts          # PWA + Tailwind
    └── dist/                   # Production build output
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No | Default: `sqlite:///./growthpilot.db` |
| `SECRET_KEY` | **Yes (prod)** | JWT signing key |
| `OPENAI_API_KEY` | No | OpenAI key (empty = mock AI mode) |
| `OPENAI_MODEL` | No | Default: `gpt-4o-mini` |
| `CORS_ORIGINS` | No | Comma-separated frontend URLs |
| `DEBUG` | No | `true` / `false` |
| `APP_ENV` | No | `development` / `production` |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | No | Default: `http://localhost:8000` |

Copy templates:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

---

## Local Development

### Prerequisites

- Python 3.12+ (3.14 tested locally)
- Node.js 20 LTS+
- OpenAI API Key (optional — mock mode without key)

### 1. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
# tests: pip install -r requirements-dev.txt

# DB migration (optional — init_db also runs on startup)
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs  
AI Health: http://localhost:8000/api/health/ai

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## Testing (STEP 6)

### Backend — 36 API tests

```powershell
cd backend
.\venv\Scripts\activate
pytest -q
```

### Deploy verification script

```powershell
cd backend
python scripts/verify_deploy.py
```

Checks: SQLite init, OpenAI (if key set), FastAPI import.

### OpenAI connection

```powershell
curl http://localhost:8000/api/health/ai
```

### React production build

```powershell
cd frontend
npm run build
```

---

## Production URLs (Live)

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://ai-tutor-project-nine.vercel.app |
| **Backend API (Render)** | https://ai-tutor-project-2.onrender.com |
| **API Base URL** | `https://ai-tutor-project-2.onrender.com` |
| **Health check** | https://ai-tutor-project-2.onrender.com/api/v1/health |
| **AI health** | https://ai-tutor-project-2.onrender.com/api/health/ai |

Frontend build uses `VITE_API_BASE_URL` → Render API (see `frontend/.env.production` and `frontend/vercel.json`).

---

## Vercel + Render Deployment (Recommended, $0)

**Frontend on Vercel** + **API on Render** — share `https://your-app.vercel.app`

Full guide: **[docs/DEPLOY_VERCEL_RENDER.md](docs/DEPLOY_VERCEL_RENDER.md)**

### Quick steps

1. **Render** — Blueprint with `render-api.yaml` → set `OPENAI_API_KEY`
2. **Vercel** — Import repo, Root Directory `frontend`, env `VITE_API_BASE_URL=https://ai-tutor-project-2.onrender.com`
3. Share your **`.vercel.app`** URL

---

## Render Deployment (Full stack on Render)

### 1. Push to GitHub

Render deploys from a Git repository. Push this project to GitHub/GitLab.

### 2. Create Blueprint

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect repository
3. Render reads `render.yaml` and creates:
   - `growthpilot-api` — Python Web Service
   - `growthpilot-web` — Static Site

### 3. Set secrets

In Render dashboard → `growthpilot-api` → **Environment**:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | Your OpenAI API key |

(`SECRET_KEY` is auto-generated by Blueprint)

### 4. Deploy URLs

After deploy succeeds:

| Service | URL |
|---------|-----|
| **Frontend (App)** | `https://growthpilot-web.onrender.com` |
| **Backend (API)** | `https://ai-tutor-project-2.onrender.com` |

Health check: `https://ai-tutor-project-2.onrender.com/api/v1/health`

> **Note:** Free tier services spin down after inactivity (~50s cold start on first request).

### 5. Production notes

- SQLite stored on **persistent disk** (`/var/data/growthpilot.db`)
- `scripts/start.sh` runs Alembic migrations before uvicorn
- CORS auto-configured from frontend hostname
- `VITE_API_BASE_URL` injected at frontend build time
- Without `OPENAI_API_KEY`, AI agents run in **mock mode**

---

## API Overview

| Path | Description |
|------|-------------|
| `POST /auth/signup` | 회원가입 |
| `POST /auth/login` | 로그인 (JWT) |
| `GET /auth/me` | 현재 사용자 |
| `GET/POST/PUT/DELETE /goal` | 목표 CRUD |
| `GET /api/v1/goals` | 목표 (legacy) |
| `GET /api/ai` | AI Agent 목록 |
| `POST /api/ai/goal/{id}/analyze` | Goal Agent |
| `POST /api/ai/planner/{id}/generate` | Planner Agent |
| `GET /api/health/ai` | OpenAI 연결 확인 |
| `GET /api/v1/health` | API + SQLite health |

---

## Development Steps (Completed)

| Step | Status | Content |
|------|--------|---------|
| 1 | ✅ | OpenAI API 연동 |
| 2 | ✅ | SQLite + SQLAlchemy + Alembic |
| 3 | ✅ | 인증 + 목표 관리 |
| 4 | ✅ | LangGraph Multi-Agent |
| 5 | ✅ | React PWA UI |
| 6 | ✅ | 테스트 + Render 배포 |

---

## License

Private project — All rights reserved.
