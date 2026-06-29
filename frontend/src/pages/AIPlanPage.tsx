import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { useGoals } from "@/hooks/useGoals";
import { ApiClientError } from "@/services/api";
import { agentService } from "@/services/agentService";
import type { GeneratePlanResult, GoalAnalysis } from "@/types";

export function AIPlanPage() {
  const { goals, isLoading } = useGoals();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [analysis, setAnalysis] = useState<GoalAnalysis | null>(null);
  const [plan, setPlan] = useState<GeneratePlanResult | null>(null);
  const [error, setError] = useState("");

  const activeGoals = goals.filter((g) => g.status === "active");

  const runAnalyze = async () => {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    try {
      setAnalysis(await agentService.analyzeGoal(selectedId));
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "분석 실패");
    } finally {
      setBusy(false);
    }
  };

  const runGenerate = async () => {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    try {
      setPlan(await agentService.generatePlan(selectedId));
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "계획 생성 실패");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="AI 계획"
        subtitle="Goal Agent 분석 → Planner Agent 월·주·일 계획"
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
          <EmptyState
            icon="◈"
            title="활성 목표가 없습니다"
            description="먼저 목표를 생성해 주세요"
            action={{ label: "목표 관리", onClick: () => (window.location.href = "/goals") }}
          />
        ) : (
          <div className="space-y-3">
            <select
              value={selectedId ?? ""}
              onChange={(e) => {
                setSelectedId(Number(e.target.value) || null);
                setAnalysis(null);
                setPlan(null);
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
              <Button size="sm" disabled={!selectedId || busy} onClick={runAnalyze}>
                1. 목표 분석
              </Button>
              <Button size="sm" disabled={!selectedId || busy} onClick={runGenerate}>
                2. 계획 생성
              </Button>
            </div>
          </div>
        )}
      </Card>

      {analysis ? (
        <Card title="Goal Agent 분석" subtitle={`현실성 ${analysis.realism_score}점`}>
          <p className="text-sm text-text leading-relaxed">{analysis.realism_analysis}</p>
          {analysis.sub_goals.length > 0 ? (
            <ul className="mt-4 space-y-2 text-sm">
              {analysis.sub_goals.map((sg) => (
                <li key={sg.title} className="rounded-xl bg-surface-muted px-3 py-2">
                  <span className="font-medium text-text">{sg.title}</span>
                  <p className="text-text-muted text-xs mt-0.5">{sg.description}</p>
                </li>
              ))}
            </ul>
          ) : null}
        </Card>
      ) : null}

      {plan ? (
        <Card title="Planner Agent 결과" subtitle={`${plan.missions.length}개 미션 · Score ${plan.updated_growth_score.toFixed(1)}`}>
          <p className="text-sm text-text-muted mb-4">{plan.memory_insight}</p>
          <div className="space-y-3">
            {plan.plans.map((p) => (
              <div key={p.id} className="rounded-xl border border-border/60 p-3">
                <span className="text-[10px] uppercase tracking-wide text-accent">{p.plan_type}</span>
                <p className="font-medium text-text text-sm mt-0.5">{p.title}</p>
                {p.content ? <p className="text-xs text-text-muted mt-1">{p.content}</p> : null}
              </div>
            ))}
          </div>
          <Link to="/missions" className="inline-block mt-4 text-sm text-accent font-medium">
            오늘의 미션 확인 →
          </Link>
        </Card>
      ) : null}
    </div>
  );
}
