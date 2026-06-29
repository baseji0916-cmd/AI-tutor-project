import { FormEvent, useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { agentService } from "@/services/agentService";
import { useAuth } from "@/stores/AuthContext";
import type { CoachFeedback, Recommendations } from "@/types";
import { COACH_PERSONALITY_OPTIONS } from "@/types";

export function CoachPage() {
  const { user } = useAuth();
  const [context, setContext] = useState("");
  const [feedback, setFeedback] = useState<CoachFeedback | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null);
  const [loading, setLoading] = useState(false);

  const personality = COACH_PERSONALITY_OPTIONS.find(
    (p) => p.value === user?.coach_personality,
  );

  useEffect(() => {
    agentService.getRecommendations().then(setRecommendations).catch(() => null);
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!context.trim()) return;
    setLoading(true);
    try {
      setFeedback(await agentService.coachFeedback(context));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text">AI 코치</h1>
        <p className="text-text-muted mt-1">
          {personality?.label} · {personality?.description}
        </p>
      </div>

      <Card title="코치에게 물어보기">
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={4}
            placeholder="오늘 기분, 고민, 목표 진행 상황을 적어주세요…"
            className="w-full px-4 py-3 rounded-xl bg-surface-muted border border-border text-text placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent/40 resize-none"
          />
          <Button type="submit" isLoading={loading} className="w-full">
            Coach Agent에게 피드백 받기
          </Button>
        </form>
      </Card>

      {feedback ? (
        <Card title="코치 피드백" subtitle={`톤: ${feedback.tone}`}>
          <p className="text-sm text-text leading-relaxed">{feedback.message}</p>
          {feedback.action_items.length > 0 ? (
            <ul className="mt-3 text-sm text-text-muted space-y-1">
              {feedback.action_items.map((a) => (
                <li key={a}>→ {a}</li>
              ))}
            </ul>
          ) : null}
        </Card>
      ) : null}

      {recommendations ? (
        <Card title="Smart Recommendation" subtitle="Recommendation Agent">
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            {(
              [
                ["추천 목표", recommendations.goals],
                ["추천 도서", recommendations.books],
                ["추천 역량", recommendations.skills],
                ["추천 습관", recommendations.habits],
              ] as const
            ).map(([label, items]) => (
              <div key={label}>
                <p className="font-medium text-text mb-1">{label}</p>
                <ul className="text-text-muted space-y-0.5">
                  {items.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
