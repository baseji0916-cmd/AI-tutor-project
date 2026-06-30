# Render "This service has been suspended" — 로그인 불가 해결

## 원인

Vercel 로그인 페이지는 API를 **Render** (`growthpilot-api.onrender.com`)로 보냅니다.

브라우저에서 `https://growthpilot-api.onrender.com/api/v1/health` 를 열었을 때  
**"This service has been suspended"** 가 보이면 API가 **완전히 꺼진 상태**입니다.

| 상태 | 의미 | 로그인 |
|------|------|--------|
| **Suspended** | Render가 서비스/계정을 중지 | ❌ 불가 |
| **Sleep** (Free 슬립) | 15분 미사용 후 첫 요청 30~60초 지연 | ✅ 가능 (대기 후) |

**Resume** 이 안 되거나 계속 Suspended 이면, 기존 `growthpilot-api` 는 복구가 어렵습니다.  
**새 Web Service** 를 만들어야 합니다.

---

## 지금 당장 쓰려면 — 로컬

로컬 API는 정상입니다 (`127.0.0.1:8000` health OK).

1. 터미널 1 — 백엔드:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
2. 터미널 2 — 프론트:
   ```bash
   cd frontend
   npm run dev
   ```
3. 브라우저: **http://127.0.0.1:5173**
4. **회원가입** 후 로그인 (로컬 DB ≠ Vercel/Render DB — 계정을 다시 만들어야 함)

---

## Vercel 로그인 복구 — 새 Render API 만들기

### 1) Render — 새 Web Service (기존 growthpilot-api 사용 X)

1. [Render Dashboard](https://dashboard.render.com) → **New +** → **Web Service**
2. GitHub 저장소 `AI-tutor-project` 연결
3. 설정:

| 항목 | 값 |
|------|-----|
| **Name** | `ai-tutor-api` (새 이름, suspended 와 별개) |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt && python scripts/verify_deploy.py` |
| **Start Command** | `bash scripts/start.sh` |
| **Plan** | Free |

4. **Environment** 변수:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | OpenAI 키 (backend/.env 와 동일) |
| `CORS_ALLOW_VERCEL` | `true` |
| `APP_ENV` | `production` |

5. **Create Web Service** → 배포 완료까지 대기 (5~10분)

6. 새 API URL 확인 (예):
   ```
   https://ai-tutor-api.onrender.com
   ```
   헬스: `https://ai-tutor-api.onrender.com/api/v1/health`  
   → `{"status":"healthy",...}` 이면 성공

> Render 계정 자체가 Suspended 이면 [Render Support](https://render.com/docs/support) 또는 결제/이메일 인증이 필요할 수 있습니다.

---

### 2) Vercel — 새 API URL 연결

**방법 A (추천) — 환경 변수만 변경**

Vercel → Project → **Settings** → **Environment Variables** (Production):

| Key | Value |
|-----|-------|
| `VITE_USE_API_PROXY` | `false` |
| `VITE_API_BASE_URL` | `https://ai-tutor-api.onrender.com` (실제 새 URL) |

→ **Redeploy** (Deployments → 최신 → Redeploy)

**방법 B — vercel.json 프록시 URL 변경**

`frontend/vercel.json` 의 `growthpilot-api.onrender.com` 을 새 URL 로 모두 바꾼 뒤 Git push → Vercel 자동 배포.

---

### 3) Vercel에서 다시 회원가입

새 Render 서비스는 **빈 SQLite DB** 입니다.  
예전 Vercel에서 만든 계정은 **없습니다**. → **회원가입** 후 로그인하세요.

---

## 확인 체크리스트

- [ ] `https://(새-API-URL)/api/v1/health` → healthy
- [ ] Vercel `VITE_API_BASE_URL` 또는 `vercel.json` 이 새 URL 과 일치
- [ ] Vercel Redeploy 완료
- [ ] Vercel 사이트에서 **새로 회원가입**
- [ ] 로그인 성공

---

## Render 대안 (Render 계정 복구 불가 시)

- Railway, Fly.io, Koyeb 등에 `backend/` 배포
- 배포 후 `VITE_API_BASE_URL` 만 Vercel 에 설정 (CORS: `CORS_ALLOW_VERCEL=true` 유지)
