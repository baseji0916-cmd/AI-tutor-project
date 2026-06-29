import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { ProgressRing } from "@/components/ui/ProgressRing";
import { Spinner } from "@/components/ui/Spinner";
import { useGoals } from "@/hooks/useGoals";
import { ApiClientError } from "@/services/api";
import { agentService } from "@/services/agentService";
import type { FutureSimulation, GrowthPredictor } from "@/types";

export function SimulationPage() {
  const { goals, isLoading } = useGoals();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [predictor, setPredictor] = useState<GrowthPredictor | null>(null);
  const [simulation, setSimulation] = useState<FutureSimulation | null>(null);
  const [error, setError] = useState("");

  const activeGoals = goals.filter((g) => g.status === "active");

  const runPredictor = async () => {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    try {
      setPredictor(await agentService.predictGrowth(selectedId));
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "예측 실패");
    } finally {
      setBusy(false);
    }
  };

  const runSimulation = async () => {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    try {
      setSimulation(await agentService.simulateFuture(selectedId));
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "시뮬레이션 실패");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="Future Simulation"
        subtitle="Growth Predictor + Scenario A · B · C"
      />

      {error ? (
        <div className="rounded-2xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-500">
          {error}
        </div>
      ) : null}

      <Card title="목표 선택">
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : activeGoals.length === 0 ? (
          <EmptyState icon="◇" title="시뮬레이션할 목표가 없습니다" />
        ) : (
          <div className="space-y-3">
            <select
              value={selectedId ?? ""}
              onChange={(e) => {
                setSelectedId(Number(e.target.value) || null);
                setPredictor(null);
                setSimulation(null);
              }}
              className="w-full px-4 py-3 rounded-xl bg-surface-muted border border-border text-text text-[15px] focus:outline-none focus:ring-2 focus:ring-accent/30"
            >
              <option value="">목표를 선택하세요</option>
              {activeGoals.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.title}
                </option>
              ))}
            </select>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" disabled={!selectedId || busy} onClick={runPredictor}>
                달성 확률 예측
              </Button>
              <Button size="sm" variant="secondary" disabled={!selectedId || busy} onClick={runSimulation}>
                Scenario A/B/C
              </Button>
            </div>
          </div>
        )}
      </Card>

      {predictor ? (
        <Card title="Growth Predictor" subtitle={`신뢰도: ${predictor.confidence_level}`}>
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <ProgressRing value={predictor.achievement_probability} label="달성 확률" />
            <div className="flex-1 space-y-3 text-sm">
              <p className="text-text-muted">
                예상 완료일:{" "}
                <span className="text-text font-medium">{predictor.predicted_completion_date}</span>
              </p>
              <div>
                <p className="font-medium text-text mb-1">핵심 요인</p>
                <ul className="text-text-muted space-y-0.5">
                  {predictor.key_factors.map((f) => (
                    <li key={f}>· {f}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </Card>
      ) : null}

      {simulation ? (
        <Card
          title="Future Simulation"
          subtitle={`달성 확률 ${simulation.achievement_probability}% · ${simulation.required_effort_hours}h`}
        >
          <div className="space-y-3">
            {simulation.scenarios.map((s, i) => (
              <div
                key={s.name}
                className="rounded-2xl border border-border/60 p-4 bg-surface-muted/30"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-accent">
                    Scenario {String.fromCharCode(65 + i)}
                  </span>
                  <span className="text-sm font-semibold tabular-nums text-text">
                    {s.achievement_probability}%
                  </span>
                </div>
                <p className="font-medium text-text text-sm mt-2">{s.name}</p>
                <p className="text-xs text-text-muted mt-1">{s.description}</p>
                <p className="text-[11px] text-text-muted mt-2">
                  완료 예상 {s.expected_completion_date} · {s.required_effort_hours}h
                </p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
