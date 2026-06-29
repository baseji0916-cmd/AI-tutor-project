import { apiRequest } from "@/services/api";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types";

const AUTH_BASE = "/api/v1/auth";

export const authService = {
  register(data: RegisterRequest): Promise<User> {
    return apiRequest<User>(`${AUTH_BASE}/register`, {
      method: "POST",
      body: data,
    });
  },

  login(data: LoginRequest): Promise<TokenResponse> {
    return apiRequest<TokenResponse>(`${AUTH_BASE}/login`, {
      method: "POST",
      body: data,
    });
  },

  getMe(): Promise<User> {
    return apiRequest<User>(`${AUTH_BASE}/me`, { auth: true });
  },
};
