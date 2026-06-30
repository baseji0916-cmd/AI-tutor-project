import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { ApiStatusBanner } from "@/components/features/auth/ApiStatusBanner";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { useAuth } from "@/stores/AuthContext";
import { ApiClientError } from "@/services/api";

export function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await login({ email, password });
    } catch (err) {
      setError(
        err instanceof ApiClientError ? err.message : "로그인에 실패했습니다.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-dvh flex flex-col bg-surface">
      <div className="flex justify-end p-4">
        <ThemeToggle />
      </div>

      <div className="flex flex-1 items-center justify-center px-4 pb-12">
        <div className="w-full max-w-[380px] space-y-8">
          <div className="text-center space-y-2">
            <h1 className="text-[2rem] font-semibold tracking-tight text-text">
              Growth<span className="text-accent">Pilot</span>
            </h1>
            <p className="text-[15px] text-text-muted">AI Growth Coach에 로그인</p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-2xl border border-border/60 bg-surface-elevated/90 backdrop-blur-xl p-6 shadow-sm"
          >
            <ApiStatusBanner />

            {error ? (
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-500">
                {error}
              </div>
            ) : null}

            <Input
              label="이메일"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
            />

            <Input
              label="비밀번호"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />

            <Button type="submit" className="w-full" isLoading={isLoading}>
              로그인
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted">
            계정이 없으신가요?{" "}
            <Link to="/register" className="text-accent hover:underline font-medium">
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
