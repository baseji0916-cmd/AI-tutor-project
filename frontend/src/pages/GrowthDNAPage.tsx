import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { agentService } from "@/services/agentService";
import type { GrowthDNAProfile } from "@/types";

export function GrowthDNAPage() {
  const [dna, setDna] = useState<GrowthDNAProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    agentService
      .getGrowthDNA()
      .then(setDna)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Spinner />
      </div>
    );
  }

  if (!dna) {
    return (
      <div className="max-w-2xl mx-auto">
        <PageHeader title="Growth DNA" subtitle="데이터를 불러올 수 없습니다" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="Growth DNA"
        subtitle={`Memory Agent · ${dna.llm_mode} 모드`}
      />

      <div className="grid sm:grid-cols-2 gap-4">
        <Card className="!p-5">
          <p className="text-xs text-text-muted uppercase tracking-wide">집중 시간</p>
          <p className="text-3xl font-semibold text-text mt-1 tabular-nums">
            {dna.focus_time}
            <span className="text-base font-normal text-text-muted ml-1">분/일</span>
          </p>
        </Card>
        <Card className="!p-5">
          <p className="text-xs text-text-muted uppercase tracking-wide">Growth Score</p>
          <p className="text-3xl font-semibold text-accent mt-1 tabular-nums">
            {dna.growth_score.toFixed(1)}
          </p>
        </Card>
      </div>

      <Card title="성공 패턴">
        {dna.success_patterns.length > 0 ? (
          <ul className="space-y-2 text-sm text-text">
            {dna.success_patterns.map((p) => (
              <li key={p} className="flex gap-2">
                <span className="text-green-500">+</span>
                {p}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-muted">AI 계획 생성 후 패턴이 학습됩니다</p>
        )}
      </Card>

      <Card title="실패 패턴">
        {dna.failure_patterns.length > 0 ? (
          <ul className="space-y-2 text-sm text-text">
            {dna.failure_patterns.map((p) => (
              <li key={p} className="flex gap-2">
                <span className="text-orange-500">−</span>
                {p}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-muted">아직 기록된 실패 패턴이 없습니다</p>
        )}
      </Card>

      {dna.preferred_feedback_style ? (
        <Card title="선호 피드백 스타일">
          <p className="text-sm text-text">{dna.preferred_feedback_style}</p>
        </Card>
      ) : null}
    </div>
  );
}
