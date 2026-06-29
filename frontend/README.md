# GrowthPilot Frontend

React + TypeScript + Tailwind CSS + PWA

## Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |

## PWA

Installable on mobile via "Add to Home Screen". Service worker auto-updates via `vite-plugin-pwa`.
