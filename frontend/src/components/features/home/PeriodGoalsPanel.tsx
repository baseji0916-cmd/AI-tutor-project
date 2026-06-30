import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { OverallGoalsStrip, PeriodTaskRow } from "@/components/features/home/PeriodTaskRow";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Spinner } from "@/components/ui/Spinner";
import { missionService } from "@/services/missionService";
import { periodRoadmapService } from "@/services/periodRoadmapService";
import type { PeriodHorizon, PeriodRoadmap, PeriodSection, PeriodTaskItem } from "@/types";
import { isLocalPeriodTaskDone, setLocalPeriodTaskDone } from "@/utils/periodTaskStorage";
import { cn } from "@/utils/cn";

interface PeriodGoalsPanelProps {
  refreshKey?: number;
  onStatsChange?: () => void;
}

const TABS: { id: PeriodHorizon; label: string; emoji: string }[] = [
  { id: "daily", label: "오늘", emoji: "☀️" },
  { id: "weekly", label: "이번 주", emoji: "📅" },
  { id: "monthly", label: "이번 달", emoji: "🗓️" },
];

function sectionProgress(section: PeriodSection): { completed: number; total: number; rate: number } {
  let completed = 0;
  for (const item of section.items) {
    if (item.mission_id) {
      if (item.status === "completed") completed += 1;
    } else if (isLocalPeriodTaskDone(item.id)) {
      completed += 1;
    }
  }
  const total = section.items.length;
  return {
    completed,
    total,
    rate: total > 0 ? (completed / total) * 100 : 0,
  };
}

export function PeriodGoalsPanel({ refreshKey = 0, onStatsChange }: PeriodGoalsPanelProps) {
  const [roadmap, setRoadmap] = useState<PeriodRoadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<PeriodHorizon>("daily");
  const [completingId, setCompletingId] = useState<string | null>(null);
  const [localTick, setLocalTick] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setRoadmap(await periodRoadmapService.get());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const activeSection = roadmap ? roadmap[tab] : null;

  const progress = useMemo(
    () => (activeSection ? sectionProgress(activeSection) : { completed: 0, total: 0, rate: 0 }),
    [activeSection, localTick],
  );

  const handleToggle = async (item: PeriodTaskItem) => {
    if (item.mission_id) {
      if (item.status === "completed") return;
      setCompletingId(item.id);
      try {
        await missionService.complete(item.mission_id);
        await load();
        onStatsChange?.();
      } finally {
        setCompletingId(null);
      }
      return;
    }

    const done = isLocalPeriodTaskDone(item.id);
    setLocalPeriodTaskDone(item.id, !done);
    setLocalTick((n) => n + 1);
  };

  return (
    <Card
      title="기간별 실행 과제"
      subtitle="전체 목표에서 오늘 · 이번 주 · 이번 달 할 일을 확인하세요"
    >
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : roadmap ? (
        <div className="space-y-5">
          <OverallGoalsStrip goals={roadmap.overall_goals} />

          <div className="flex gap-2 p-1 rounded-xl bg-surface-muted/60">
            {TABS.map(({ id, label, emoji }) => {
              const sec = roadmap[id];
              const { rate } = sectionProgress(sec);
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setTab(id)}
                  className={cn(
                    "flex-1 rounded-lg px-2 py-2.5 text-center transition-all",
                    tab === id
                      ? "bg-surface-elevated shadow-sm border border-border/40"
                      : "text-text-muted hover:text-text",
                  )}
                >
                  <span className="text-lg">{emoji}</span>
                  <p className="text-xs font-medium mt-0.5">{label}</p>
                  <p className="text-[10px] text-text-muted tabular-nums">{Math.round(rate)}%</p>
                </button>
              );
            })}
          </div>

          {activeSection ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <p className="text-sm font-semibold text-text">{activeSection.label}</p>
                  <p className="text-xs text-text-muted">{activeSection.period_label}</p>
                </div>
                {activeSection.is_template ? (
                  <span className="text-[10px] px-2 py-1 rounded-full bg-amber-500/10 text-amber-600 font-medium">
                    AI 계획 전 · 추천 템플릿
                  </span>
                ) : null}
              </div>

              <ProgressBar
                value={progress.rate}
                label={`${progress.completed} / ${progress.total} 완료`}
              />

              <div className="space-y-2">
                {activeSection.items.map((item) => (
                  <PeriodTaskRow
                    key={item.id}
                    item={item}
                    completing={completingId === item.id}
                    onToggle={handleToggle}
                  />
                ))}
              </div>

              {activeSection.is_template ? (
                <div className="rounded-xl bg-accent/5 border border-accent/20 p-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <p className="text-xs text-text-muted">
                    AI가 월·주·일 계획을 생성하면 실제 미션으로 자동 전환됩니다
                  </p>
                  <Link to="/ai-plan">
                    <Button size="sm">AI 계획 생성</Button>
                  </Link>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : (
        <p className="text-sm text-text-muted text-center py-8">과제를 불러오지 못했습니다</p>
      )}
    </Card>
  );
}
