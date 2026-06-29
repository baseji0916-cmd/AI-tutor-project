import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { agentService } from "@/services/agentService";
import type { GrowthStory, TimelineEvent } from "@/types";

export function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [story, setStory] = useState<GrowthStory | null>(null);
  const [loading, setLoading] = useState(true);
  const [storyLoading, setStoryLoading] = useState(false);

  useEffect(() => {
    agentService
      .listTimeline()
      .then(setEvents)
      .finally(() => setLoading(false));
  }, []);

  const loadStory = async () => {
    setStoryLoading(true);
    try {
      setStory(await agentService.getGrowthStory());
    } finally {
      setStoryLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="Growth Timeline"
        subtitle="성장 과정 기록 · Growth Story"
        action={
          <Button size="sm" onClick={loadStory} isLoading={storyLoading}>
            Growth Story
          </Button>
        }
      />

      {story ? (
        <Card title="Growth Story" subtitle={`${story.llm_mode} 모드`}>
          <p className="text-[15px] text-text leading-relaxed whitespace-pre-line">
            {story.story}
          </p>
          {story.highlights.length > 0 ? (
            <ul className="mt-4 flex flex-wrap gap-2">
              {story.highlights.map((h) => (
                <li
                  key={h}
                  className="text-[11px] px-2.5 py-1 rounded-full bg-surface-muted text-text-muted"
                >
                  {h}
                </li>
              ))}
            </ul>
          ) : null}
        </Card>
      ) : null}

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      ) : events.length === 0 ? (
        <Card>
          <p className="text-center text-text-muted py-12 text-sm">
            아직 타임라인 기록이 없습니다
          </p>
        </Card>
      ) : (
        <div className="relative pl-5 border-l border-border/80 space-y-6">
          {events.map((e) => (
            <div key={e.id} className="relative pl-4">
              <span className="absolute -left-[1.35rem] top-1.5 h-2.5 w-2.5 rounded-full bg-accent ring-4 ring-surface" />
              <p className="text-[11px] text-text-muted tabular-nums">
                {e.occurred_at.slice(0, 16).replace("T", " ")}
              </p>
              <h3 className="font-medium text-text text-[15px] mt-0.5">{e.title}</h3>
              {e.description ? (
                <p className="text-sm text-text-muted mt-1">{e.description}</p>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
