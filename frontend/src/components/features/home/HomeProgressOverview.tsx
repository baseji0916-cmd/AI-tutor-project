import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { ProgressRing } from "@/components/ui/ProgressRing";
import type { DashboardStats, Goal } from "@/types";

interface HomeProgressOverviewProps {
  stats: DashboardStats;
  goals: Goal[];
}

export function HomeProgressOverview({ stats, goals }: HomeProgressOverviewProps) {
  const activeGoals = goals.filter((g) => g.status === "active");
  const todayRate =
    stats.today_missions_total > 0
      ? (stats.today_missions_completed / stats.today_missions_total) * 100
      : 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <Card className="!p-4 sm:!p-5 flex flex-col items-center justify-center">
          <ProgressRing value={stats.progress_rate} size={72} stroke={6} />
          <p className="text-[11px] text-text-muted mt-2">전체 미션 진행률</p>
        </Card>
        <Card className="!p-4 sm:!p-5 flex flex-col items-center justify-center">
          <ProgressRing value={stats.achievement_rate} size={72} stroke={6} />
          <p className="text-[11px] text-text-muted mt-2">목표 달성률</p>
        </Card>
        <Card className="!p-4 sm:!p-5 flex flex-col items-center justify-center">
          <ProgressRing value={todayRate} size={72} stroke={6} />
          <p className="text-[11px] text-text-muted mt-2">오늘 과제 달성</p>
        </Card>
        <Card className="!p-4 sm:!p-5">
          <p className="text-[11px] text-text-muted uppercase tracking-wide">Growth Score</p>
          <p className="text-2xl sm:text-3xl font-semibold text-text mt-1 tabular-nums">
            {stats.growth_score.toFixed(1)}
          </p>
          <p className="text-[11px] text-text-muted mt-2">
            활성 목표 {stats.active_goals}개
          </p>
        </Card>
      </div>

      {activeGoals.length > 0 ? (
        <Card title="목표별 진행률">
          <div className="space-y-4">
            {activeGoals.slice(0, 5).map((goal) => (
              <ProgressBar
                key={goal.id}
                label={goal.title}
                value={goal.progress_rate}
              />
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
