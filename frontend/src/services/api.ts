import type { ApiError } from "@/types";
import { clearStoredToken, getApiBaseUrl, getStoredToken } from "@/utils/storage";

export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  auth?: boolean;
};

/** Central HTTP client — all backend calls go through here */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, auth = false, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    ...(customHeaders as Record<string, string>),
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getStoredToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const url = `${getApiBaseUrl()}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...rest,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiClientError(
      "서버에 연결할 수 없습니다. API 서버 상태를 확인해 주세요.",
      0,
    );
  }

  if (response.status === 503) {
    throw new ApiClientError(
      "API 서버가 일시 중지되었습니다. Render Dashboard에서 서비스를 Resume한 뒤 다시 시도해 주세요.",
      503,
    );
  }

  if (response.status === 401 && auth) {
    clearStoredToken();
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const errorData = (await response.json()) as ApiError;
      if (typeof errorData.detail === "string") {
        message = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        message = errorData.detail.map((e) => e.msg).join(", ");
      }
    } catch {
      // use default message
    }
    throw new ApiClientError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
