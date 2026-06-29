import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { useAuth } from "@/stores/AuthContext";
import { useTheme } from "@/hooks/useTheme";
import { agentService } from "@/services/agentService";
import { ApiClientError } from "@/services/api";
import type { PersonalityInfo } from "@/types";
import { cn } from "@/utils/cn";

export function SettingsPage() {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const [personality, setPersonality] = useState<PersonalityInfo | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    agentService.getPersonality().then(setPersonality).catch(() => null);
  }, []);

  const handlePersonality = async (id: string) => {
    setSaving(true);
    setMessage("");
    try {
      setPersonality(await agentService.updatePersonality(id));
      setMessage("코치 성격이 변경되었습니다");
    } catch (e) {
      setMessage(e instanceof ApiClientError ? e.message : "변경 실패");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-lg mx-auto">
      <PageHeader title="설정" subtitle="계정, 테마, AI Tutor 성격" />

      <Card title="계정">
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-text-muted">이름</dt>
            <dd className="text-text font-medium">{user?.full_name ?? user?.username}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-text-muted">이메일</dt>
            <dd className="text-text">{user?.email}</dd>
          </div>
        </dl>
      </Card>

      <Card title="화면">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-text">다크 모드</p>
            <p className="text-xs text-text-muted mt-0.5">
              현재: {theme === "dark" ? "다크" : "라이트"}
            </p>
          </div>
          <ThemeToggle />
        </div>
      </Card>

      <Card title="AI Tutor 성격">
        {!personality ? (
          <div className="flex justify-center py-6">
            <Spinner />
          </div>
        ) : (
          <div className="space-y-2">
            {personality.available.map((opt) => (
              <button
                key={opt.id}
                type="button"
                disabled={saving}
                onClick={() => handlePersonality(opt.id)}
                className={cn(
                  "w-full text-left rounded-xl px-4 py-3 border transition-all",
                  personality.current === opt.id
                    ? "border-accent bg-accent/10"
                    : "border-border/60 hover:bg-surface-muted/50",
                )}
              >
                <p className="text-sm font-medium text-text">{opt.label_ko}</p>
                <p className="text-xs text-text-muted mt-0.5">{opt.description}</p>
              </button>
            ))}
          </div>
        )}
        {message ? <p className="text-xs text-accent mt-3">{message}</p> : null}
      </Card>

      <Button variant="danger" className="w-full" onClick={logout}>
        로그아웃
      </Button>
    </div>
  );
}
