import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { ProgressRing } from "@/components/ui/ProgressRing";
import { Spinner } from "@/components/ui/Spinner";
import { useGoals } from "@/hooks/useGoals";
import { goalService } from "@/services/goalService";
import type { DashboardStats } from "@/types";
import { GOAL_STATUS_LABELS } from "@/types";

export function ProgressPage() {
  const { goals, isLoading } = useGoals();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    goalService.getDashboardStats().then(setStats).catch(() => null);
  }, []);

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader title="진행률" subtitle="목표와 미션 달성 현황" />

      {stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Card className="!p-4 flex flex-col items-center">
            <ProgressRing value={stats.progress_rate} label="미션 진행률" />
          </Card>
          <Card className="!p-4 flex flex-col items-center">
            <ProgressRing value={stats.achievement_rate} label="목표 달성률" />
          </Card>
          <Card className="!p-4 col-span-2 sm:col-span-2 flex flex-col justify-center">
            <p className="text-xs text-text-muted uppercase tracking-wide">Growth Score</p>
            <p className="text-4xl font-semibold text-text mt-1 tabular-nums">
              {stats.growth_score.toFixed(1)}
            </p>
            <p className="text-sm text-text-muted mt-2">
              오늘 미션 {stats.today_missions_completed}/{stats.today_missions_total} · 활성 목표{" "}
              {stats.active_goals}개
            </p>
          </Card>
        </div>
      ) : (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      )}

      <Card title="목표별 진행률">
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : goals.length === 0 ? (
          <p className="text-sm text-text-muted text-center py-8">
            등록된 목표가 없습니다.{" "}
            <Link to="/goals" className="text-accent">
              목표 추가
            </Link>
          </p>
        ) : (
          <div className="space-y-4">
            {goals.map((g) => (
              <div key={g.id}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium text-text truncate pr-2">{g.title}</span>
                  <span className="text-text-muted shrink-0 tabular-nums">
                    {g.progress_rate}%
                  </span>
                </div>
                <div className="h-2 rounded-full bg-surface-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-accent transition-all duration-500"
                    style={{ width: `${g.progress_rate}%` }}
                  />
                </div>
                <p className="text-[11px] text-text-muted mt-1">
                  {GOAL_STATUS_LABELS[g.status]} · 우선순위 {g.priority}
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
