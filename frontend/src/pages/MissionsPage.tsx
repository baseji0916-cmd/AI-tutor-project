import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { agentService } from "@/services/agentService";
import { missionService } from "@/services/missionService";
import type { FailureRecovery, Mission } from "@/types";
import { MISSION_STATUS_LABELS } from "@/types";
import { cn } from "@/utils/cn";

export function MissionsPage() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [failureResult, setFailureResult] = useState<FailureRecovery | null>(null);

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
  }, [load]);

  const handleComplete = async (id: number) => {
    await missionService.complete(id);
    await load();
  };

  const handleFail = async (id: number) => {
    const notes = prompt("실패 사유 (선택):") ?? "";
    await missionService.fail(id, notes || undefined);
    const analysis = await agentService.analyzeFailure(id, notes || undefined, true);
    setFailureResult(analysis);
    await load();
  };

  const todayLabel = new Date().toLocaleDateString("ko-KR", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader title="오늘의 미션" subtitle={todayLabel} />

      {failureResult ? (
        <Card title="Failure Analyzer" subtitle={failureResult.summary}>
          <div className="space-y-3 text-sm">
            <div>
              <p className="font-medium text-text mb-1">원인</p>
              <ul className="text-text-muted space-y-0.5">
                {failureResult.root_causes.map((c) => (
                  <li key={c}>· {c}</li>
                ))}
              </ul>
            </div>
            {failureResult.replanned && failureResult.replan ? (
              <div className="rounded-xl bg-accent/5 border border-accent/20 p-3">
                <p className="text-xs font-medium text-accent">Auto Replanner 실행됨</p>
                <p className="text-xs text-text-muted mt-1">{failureResult.replan.revision_summary}</p>
              </div>
            ) : null}
            {failureResult.dna_updated ? (
              <Link to="/growth-dna" className="text-xs text-accent">
                Growth DNA 확인 →
              </Link>
            ) : null}
          </div>
        </Card>
      ) : null}

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      ) : missions.length === 0 ? (
        <Card>
          <div className="text-center py-12 space-y-3">
            <span className="text-4xl opacity-60">✓</span>
            <p className="text-sm text-text-muted">오늘 예정된 미션이 없습니다</p>
            <Link to="/ai-plan">
              <Button size="sm" variant="secondary">
                AI 계획 생성
              </Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="space-y-3">
          {missions.map((m) => (
            <div
              key={m.id}
              className="rounded-2xl border border-border/60 bg-surface-elevated p-4"
            >
              <span
                className={cn(
                  "text-[11px] px-2 py-0.5 rounded-full font-medium",
                  m.status === "completed" && "bg-green-500/10 text-green-600",
                  m.status === "pending" && "bg-accent/10 text-accent",
                  m.status === "failed" && "bg-red-500/10 text-red-500",
                )}
              >
                {MISSION_STATUS_LABELS[m.status]}
              </span>
              <h3 className="font-medium text-text mt-2 text-[15px]">{m.title}</h3>
              <p className="text-xs text-text-muted mt-1">{m.goal_title}</p>
              {m.description ? (
                <p className="text-sm text-text-muted mt-2">{m.description}</p>
              ) : null}
              {m.status === "pending" ? (
                <div className="flex gap-2 mt-3">
                  <Button size="sm" onClick={() => handleComplete(m.id)}>
                    완료
                  </Button>
                  <Button size="sm" variant="secondary" onClick={() => handleFail(m.id)}>
                    실패 · 분석
                  </Button>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
