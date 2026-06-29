import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Spinner } from "@/components/ui/Spinner";
import { missionService } from "@/services/missionService";
import type { Mission } from "@/types";
import { MISSION_STATUS_LABELS } from "@/types";
import { cn } from "@/utils/cn";

interface TodayTasksPanelProps {
  onStatsChange?: () => void;
  refreshKey?: number;
}

export function TodayTasksPanel({ onStatsChange, refreshKey = 0 }: TodayTasksPanelProps) {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [completingId, setCompletingId] = useState<number | null>(null);
  const [batchCount, setBatchCount] = useState("");
  const [batchLoading, setBatchLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setMissions(await missionService.listToday());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const pending = missions.filter((m) => m.status === "pending");
  const completed = missions.filter((m) => m.status === "completed");
  const todayRate =
    missions.length > 0 ? (completed.length / missions.length) * 100 : 0;

  const handleComplete = async (id: number) => {
    setCompletingId(id);
    try {
      await missionService.complete(id);
      await load();
      onStatsChange?.();
    } finally {
      setCompletingId(null);
    }
  };

  const handleBatchComplete = async () => {
    const count = parseInt(batchCount, 10);
    if (!count || count < 1 || pending.length === 0) return;

    setBatchLoading(true);
    try {
      const toComplete = pending.slice(0, Math.min(count, pending.length));
      for (const mission of toComplete) {
        await missionService.complete(mission.id);
      }
      setBatchCount("");
      await load();
      onStatsChange?.();
    } finally {
      setBatchLoading(false);
    }
  };

  const todayLabel = new Date().toLocaleDateString("ko-KR", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <Card title="오늘의 과제" subtitle={todayLabel}>
      {loading ? (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      ) : missions.length === 0 ? (
        <div className="text-center py-8 space-y-3">
          <p className="text-sm text-text-muted">오늘 예정된 과제가 없습니다</p>
          <Link to="/ai-plan">
            <Button size="sm" variant="secondary">
              AI 계획 생성하기
            </Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <ProgressBar
              value={todayRate}
              label={`${completed.length} / ${missions.length} 완료`}
              className="flex-1"
            />
          </div>

          {pending.length > 0 ? (
            <div className="flex flex-wrap items-end gap-2 rounded-xl bg-surface-muted/50 p-3">
              <div className="flex-1 min-w-[120px]">
                <label className="block text-[11px] text-text-muted mb-1">
                  완료 개수 한번에 입력
                </label>
                <input
                  type="number"
                  min={1}
                  max={pending.length}
                  value={batchCount}
                  onChange={(e) => setBatchCount(e.target.value)}
                  placeholder={`1 ~ ${pending.length}`}
                  className="w-full h-10 px-3 rounded-lg bg-surface-elevated border border-border/60 text-sm text-text focus:outline-none focus:ring-2 focus:ring-accent/30"
                />
              </div>
              <Button
                size="sm"
                onClick={handleBatchComplete}
                isLoading={batchLoading}
                disabled={!batchCount || parseInt(batchCount, 10) < 1}
              >
                {batchCount ? `${Math.min(parseInt(batchCount, 10) || 0, pending.length)}개 완료` : "적용"}
              </Button>
            </div>
          ) : null}

          <div className="space-y-2">
            {missions.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "flex items-center gap-3 rounded-xl border border-border/60 p-3",
                  m.status === "completed" && "bg-green-500/5 border-green-500/20",
                )}
              >
                <button
                  type="button"
                  disabled={m.status !== "pending" || completingId === m.id}
                  onClick={() => handleComplete(m.id)}
                  className={cn(
                    "shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all",
                    m.status === "completed"
                      ? "border-green-500 bg-green-500 text-white"
                      : "border-border hover:border-accent hover:bg-accent/10",
                    m.status !== "pending" && "cursor-default",
                  )}
                  aria-label={m.status === "completed" ? "완료됨" : "완료하기"}
                >
                  {m.status === "completed" ? "✓" : completingId === m.id ? "…" : ""}
                </button>

                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      "text-sm font-medium truncate",
                      m.status === "completed" ? "text-text-muted line-through" : "text-text",
                    )}
                  >
                    {m.title}
                  </p>
                  <p className="text-[11px] text-text-muted truncate">{m.goal_title}</p>
                </div>

                <span
                  className={cn(
                    "text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0",
                    m.status === "completed" && "bg-green-500/10 text-green-600",
                    m.status === "pending" && "bg-accent/10 text-accent",
                    m.status === "failed" && "bg-red-500/10 text-red-500",
                  )}
                >
                  {MISSION_STATUS_LABELS[m.status]}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
