import type { Goal, GoalStatus } from "@/types";
import { GOAL_STATUS_LABELS, PRIORITY_LABELS } from "@/types";
import { cn } from "@/utils/cn";

interface GoalCardProps {
  goal: Goal;
  onEdit: (goal: Goal) => void;
  onDelete: (id: number) => void;
  onStatusChange: (id: number, status: GoalStatus) => void;
}

const statusColors: Record<GoalStatus, string> = {
  active: "bg-accent/10 text-accent",
  completed: "bg-green-500/10 text-green-500",
  paused: "bg-yellow-500/10 text-yellow-600",
  abandoned: "bg-red-500/10 text-red-500",
};

export function GoalCard({ goal, onEdit, onDelete, onStatusChange }: GoalCardProps) {
  const daysLeft = Math.ceil(
    (new Date(goal.end_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <div className="rounded-2xl border border-border/60 bg-surface-elevated p-5 transition-all hover:shadow-md active:scale-[0.99]">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span
          className={cn(
            "text-[11px] font-medium px-2 py-0.5 rounded-full",
            statusColors[goal.status],
          )}
        >
          {GOAL_STATUS_LABELS[goal.status]}
        </span>
        <span className="text-[11px] text-text-muted px-2 py-0.5 rounded-full bg-surface-muted">
          {PRIORITY_LABELS[goal.priority] ?? `P${goal.priority}`}
        </span>
      </div>

      <h3 className="text-[15px] font-semibold text-text">{goal.title}</h3>
      {goal.description ? (
        <p className="text-sm text-text-muted mt-1 line-clamp-2">{goal.description}</p>
      ) : null}

      <div className="mt-4 space-y-1.5">
        <div className="flex justify-between text-[11px] text-text-muted">
          <span>진행률</span>
          <span className="tabular-nums">{goal.progress_rate}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-surface-muted overflow-hidden">
          <div
            className="h-full rounded-full bg-accent transition-all duration-500"
            style={{ width: `${Math.min(goal.progress_rate, 100)}%` }}
          />
        </div>
      </div>

      <p className="mt-3 text-[11px] text-text-muted">
        {goal.start_date} ~ {goal.end_date}
        {goal.status === "active" && daysLeft >= 0 ? ` · D-${daysLeft}` : ""}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {goal.status === "active" ? (
          <button
            type="button"
            onClick={() => onStatusChange(goal.id, "completed")}
            className="text-[11px] px-3 py-1.5 rounded-lg bg-green-500/10 text-green-600"
          >
            완료
          </button>
        ) : null}
        <button
          type="button"
          onClick={() => onEdit(goal)}
          className="text-[11px] px-3 py-1.5 rounded-lg bg-surface-muted text-text-muted"
        >
          수정
        </button>
        <button
          type="button"
          onClick={() => onDelete(goal.id)}
          className="text-[11px] px-3 py-1.5 rounded-lg text-red-500"
        >
          삭제
        </button>
      </div>
    </div>
  );
}
