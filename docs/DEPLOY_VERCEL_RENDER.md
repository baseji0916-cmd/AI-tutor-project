# Vercel + Render 무료 배포 가이드

프론트(React)는 **Vercel**, API(FastAPI)는 **Render**에 올리는 $0 구성입니다.

```
사용자 → https://your-app.vercel.app  (Vercel)
              ↓ API 호출
         https://growthpilot-api.onrender.com  (Render)
```

---

## 1단계: Render — 백엔드 API ($0)

### 방법 A — Blueprint (추천)

1. [Render Dashboard](https://dashboard.render.com) → **New +** → **Blueprint**
2. GitHub 저장소 `AI-tutor-project` 연결
3. **`render-api.yaml`** 사용 (API만 생성, 프론트 제외)
4. **Apply**

### 방법 B — 수동 Web Service

1. **New +** → **Web Service** → 저장소 연결
2. Root Directory: `backend`
3. Build: `pip install -r requirements.txt -r requirements-ai.txt`
4. Start: `bash scripts/start.sh`
5. Plan: **Free**

> **Free 플랜 참고:** 디스크 없이 SQLite 사용 → 재배포 시 DB 초기화될 수 있음. 데모/테스트용으로 충분합니다.

### API 환경 변수 (필수)

`growthpilot-api` → **Environment**:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `CORS_ALLOW_VERCEL` | `true` (기본값, Vercel 도메인 허용) |

배포 후 API URL 확인 (예):

```
https://growthpilot-api.onrender.com
```

헬스 체크: `https://growthpilot-api.onrender.com/api/v1/health`

> Render Free: 15분 미사용 시 슬립 → 첫 API 요청 30~60초 걸릴 수 있음

---

## 2단계: Vercel — 프론트엔드 ($0)

1. [vercel.com](https://vercel.com) → **Sign Up** → **Continue with GitHub**
2. **Add New…** → **Project**
3. 저장소 **`AI-tutor-project`** Import
4. 프로젝트 설정:

| 항목 | 값 |
|------|-----|
| **Root Directory** | `frontend` |
| **Framework Preset** | Vite |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

5. **Environment Variables** (Production):

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://growthpilot-api.onrender.com` |

(API URL 끝에 `/` 없이, Render 배포 후 실제 URL로 입력)

6. **Deploy**

---

## 3단계: 공유 URL

배포 완료 후 **이 주소를 다른 사람에게 공유**:

```
https://<프로젝트명>.vercel.app
```

Vercel Dashboard → Project → **Domains** 에서 확인

---

## 동작 확인

1. Vercel URL 접속 → 회원가입
2. AI 코치에 목표 입력
3. API가 슬립 상태면 첫 요청 30~60초 대기 후 정상

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| CORS 오류 | Render에 `CORS_ALLOW_VERCEL=true` 확인 |
| API 연결 실패 | Vercel `VITE_API_BASE_URL`이 Render API URL과 일치하는지 확인 |
| AI mock만 동작 | Render `OPENAI_API_KEY` 설정 후 Manual Deploy |
| 404 on 새로고침 | `frontend/vercel.json` SPA rewrite 포함 여부 확인 |

---

## GitHub 푸시 후 자동 배포

- **Vercel**: `main` 브랜치 push → 프론트 자동 재배포
- **Render**: `main` 브랜치 push → API 자동 재배포

환경 변수 변경 시 각 대시보드에서 저장 후 재배포하세요.
