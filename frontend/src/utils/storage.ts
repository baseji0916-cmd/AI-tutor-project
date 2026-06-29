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

export function getApiBaseUrl(): string {
  // Vite dev server proxies /api, /auth, /goal to the backend
  if (import.meta.env.DEV) {
    return "";
  }
  const raw = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  const trimmed = String(raw).trim().replace(/\/$/, "");
  // Render blueprint may inject hostname only (no scheme)
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }
  return `https://${trimmed}`;
}
