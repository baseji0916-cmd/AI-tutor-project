import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { CoachPersonalitySelect } from "@/components/features/auth/CoachPersonalitySelect";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { useAuth } from "@/stores/AuthContext";
import { ApiClientError } from "@/services/api";
import type { CoachPersonality } from "@/types";

export function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [coachPersonality, setCoachPersonality] =
    useState<CoachPersonality>("teacher");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await register({
        email,
        username,
        password,
        full_name: fullName || undefined,
        coach_personality: coachPersonality,
      });
    } catch (err) {
      setError(
        err instanceof ApiClientError ? err.message : "회원가입에 실패했습니다.",
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

      <div className="flex flex-1 items-center justify-center px-4 py-8">
        <div className="w-full max-w-lg space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-text">
              시작하기
            </h1>
            <p className="text-text-muted">AI 코치와 함께 성장 여정을 시작하세요</p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-2xl border border-border bg-surface-elevated p-6 shadow-sm"
          >
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
            />

            <Input
              label="사용자명"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              pattern="^[a-zA-Z0-9_]+$"
              title="영문, 숫자, 밑줄(_)만 사용 가능"
              placeholder="my_username"
            />

            <Input
              label="이름 (선택)"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="홍길동"
            />

            <Input
              label="비밀번호"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="8자 이상"
            />

            <CoachPersonalitySelect
              value={coachPersonality}
              onChange={setCoachPersonality}
            />

            <Button type="submit" className="w-full" isLoading={isLoading}>
              회원가입
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted">
            이미 계정이 있으신가요?{" "}
            <Link to="/login" className="text-accent hover:underline font-medium">
              로그인
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
