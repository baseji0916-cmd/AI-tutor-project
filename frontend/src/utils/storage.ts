const TOKEN_KEY = "growthpilot_token";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** Render production API (direct calls when proxy is disabled). */
const PRODUCTION_API_BASE_URL = "https://ai-tutor-project-2.onrender.com";

export function getApiBaseUrl(): string {
  // Dev + Vercel production proxy: same-origin (/api, /auth, /goal → Render)
  if (import.meta.env.DEV || import.meta.env.VITE_USE_API_PROXY === "true") {
    return "";
  }

  const raw =
    import.meta.env.VITE_API_BASE_URL ??
    (import.meta.env.PROD ? PRODUCTION_API_BASE_URL : "http://localhost:8000");
  const trimmed = String(raw).trim().replace(/\/$/, "");
  if (!trimmed || trimmed === "http://localhost:8000") {
    return PRODUCTION_API_BASE_URL;
  }
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }
  return `https://${trimmed}`;
}
