import { Link } from "react-router-dom";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { cn } from "@/utils/cn";
import type { PeriodTaskItem } from "@/types";
import { isLocalPeriodTaskDone } from "@/utils/periodTaskStorage";

interface PeriodTaskRowProps {
  item: PeriodTaskItem;
  completing?: boolean;
  onToggle: (item: PeriodTaskItem) => void;
}

function effectiveStatus(item: PeriodTaskItem): "pending" | "completed" | "failed" {
  if (item.mission_id) {
    return item.status as "pending" | "completed" | "failed";
  }
  return isLocalPeriodTaskDone(item.id) ? "completed" : "pending";
}

const SOURCE_LABEL: Record<string, string> = {
  mission: "실행",
  plan: "계획",
  template: "템플릿",
  goal: "목표",
};

export function PeriodTaskRow({ item, completing, onToggle }: PeriodTaskRowProps) {
  const status = effectiveStatus(item);
  const isDone = status === "completed";

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-xl border border-border/60 p-3",
        isDone && "bg-green-500/5 border-green-500/20",
      )}
    >
      <button
        type="button"
        disabled={status === "failed" || completing}
        onClick={() => onToggle(item)}
        className={cn(
          "shrink-0 w-8 h-8 mt-0.5 rounded-full border-2 flex items-center justify-center transition-all",
          isDone
            ? "border-green-500 bg-green-500 text-white"
            : "border-border hover:border-accent hover:bg-accent/10",
          status === "failed" && "opacity-50 cursor-not-allowed",
        )}
        aria-label={isDone ? "완료됨" : "완료하기"}
      >
        {isDone ? "✓" : completing ? "…" : ""}
      </button>

      <div className="flex-1 min-w-0 space-y-1">
        <p
          className={cn(
            "text-sm font-medium",
            isDone ? "text-text-muted line-through" : "text-text",
          )}
        >
          {item.title}
        </p>
        {item.description ? (
          <p className="text-xs text-text-muted line-clamp-2">{item.description}</p>
        ) : null}
        <div className="flex flex-wrap items-center gap-2 text-[10px] text-text-muted">
          {item.goal_title ? <span>{item.goal_title}</span> : null}
          <span className="px-1.5 py-0.5 rounded bg-surface-muted">
            {SOURCE_LABEL[item.source] ?? item.source}
          </span>
        </div>
      </div>
    </div>
  );
}

interface OverallGoalsStripProps {
  goals: { id: number; title: string; progress_rate: number; end_date: string }[];
}

export function OverallGoalsStrip({ goals }: OverallGoalsStripProps) {
  if (goals.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border/80 p-4 text-center space-y-2">
        <p className="text-sm text-text-muted">설정된 목표가 없습니다</p>
        <Link to="/goals" className="text-sm text-accent hover:underline">
          목표 추가하기 →
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-xs font-medium text-text-muted uppercase tracking-wide">
        전체 목표 → 기간별 실행
      </p>
      {goals.map((goal) => (
        <ProgressBar
          key={goal.id}
          label={`${goal.title} · 마감 ${goal.end_date}`}
          value={goal.progress_rate}
        />
      ))}
    </div>
  );
}
