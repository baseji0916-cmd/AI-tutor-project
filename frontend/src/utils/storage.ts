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

/** Render production API (fallback when VITE_API_BASE_URL is unset at build time). */
const PRODUCTION_API_BASE_URL = "https://growthpilot-api.onrender.com";

export function getApiBaseUrl(): string {
  // Vite dev server proxies /api, /auth, /goal to the backend
  if (import.meta.env.DEV) {
    return "";
  }
  const raw =
    import.meta.env.VITE_API_BASE_URL ??
    (import.meta.env.PROD ? PRODUCTION_API_BASE_URL : "http://localhost:8000");
  const trimmed = String(raw).trim().replace(/\/$/, "");
  if (!trimmed || trimmed === "http://localhost:8000") {
    return PRODUCTION_API_BASE_URL;
  }
  // Render blueprint may inject hostname only (no scheme)
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }
  return `https://${trimmed}`;
}
