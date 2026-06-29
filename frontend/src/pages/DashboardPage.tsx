import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AICoachChat } from "@/components/features/coach/AICoachChat";
import { HomeProgressOverview } from "@/components/features/home/HomeProgressOverview";
import { TodayTasksPanel } from "@/components/features/home/TodayTasksPanel";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { mainNavItems } from "@/config/navigation";
import { goalService } from "@/services/goalService";
import { useAuth } from "@/stores/AuthContext";
import type { DashboardStats, Goal } from "@/types";
import { COACH_PERSONALITY_OPTIONS } from "@/types";

const quickLinks = mainNavItems.filter((i) =>
  ["/ai-plan", "/missions", "/progress"].includes(i.to),
);

export function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [tasksRefreshKey, setTasksRefreshKey] = useState(0);

  const refresh = useCallback(async () => {
    try {
      const [statsData, goalsData] = await Promise.all([
        goalService.getDashboardStats(),
        goalService.list(),
      ]);
      setStats(statsData);
      setGoals(goalsData);
    } catch {
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleGoalCreated = useCallback(async () => {
    await refresh();
    setTasksRefreshKey((k) => k + 1);
  }, [refresh]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const personality = COACH_PERSONALITY_OPTIONS.find(
    (p) => p.value === user?.coach_personality,
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title={`안녕하세요, ${user?.full_name ?? user?.username}님`}
        subtitle={`${personality?.label ?? "AI"} 코치와 함께 성장 중`}
      />

      <AICoachChat variant="compact" onGoalCreated={handleGoalCreated} />

      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : stats ? (
        <HomeProgressOverview stats={stats} goals={goals} />
      ) : null}

      <TodayTasksPanel onStatsChange={refresh} refreshKey={tasksRefreshKey} />

      <div>
        <h2 className="text-sm font-medium text-text-muted uppercase tracking-wide mb-3">
          빠른 실행
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Link
            to="/tutor"
            className="rounded-2xl border border-accent/30 bg-accent/5 p-4 hover:bg-accent/10 transition-colors active:scale-[0.98]"
          >
            <span className="text-2xl">◑</span>
            <p className="text-sm font-medium text-text mt-2">AI 코치 전체화면</p>
          </Link>
          {quickLinks.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="rounded-2xl border border-border/60 bg-surface-elevated p-4 hover:bg-surface-muted/50 transition-colors active:scale-[0.98]"
            >
              <span className="text-2xl">{item.icon}</span>
              <p className="text-sm font-medium text-text mt-2">{item.label}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
