import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authService } from "@/services/authService";
import type { LoginRequest, RegisterRequest, User } from "@/types";
import {
  clearStoredToken,
  getStoredToken,
  setStoredToken,
} from "@/utils/storage";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setUser(null);
      return;
    }
    const me = await authService.getMe();
    setUser(me);
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        if (getStoredToken()) {
          await refreshUser();
        }
      } catch {
        clearStoredToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    void bootstrap();
  }, [refreshUser]);

  const login = useCallback(async (data: LoginRequest) => {
    const token = await authService.login(data);
    setStoredToken(token.access_token);
    await refreshUser();
  }, [refreshUser]);

  const register = useCallback(async (data: RegisterRequest) => {
    await authService.register(data);
    await login({ email: data.email, password: data.password });
  }, [login]);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
