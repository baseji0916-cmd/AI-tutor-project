import { AICoachChat } from "@/components/features/coach/AICoachChat";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAuth } from "@/stores/AuthContext";
import { COACH_PERSONALITY_OPTIONS } from "@/types";

/** AI Coach — unified goal setup + tutoring (same chat as dashboard). */
export function TutorPage() {
  const { user } = useAuth();
  const personality = COACH_PERSONALITY_OPTIONS.find(
    (p) => p.value === user?.coach_personality,
  );

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="AI 코치"
        subtitle={`${personality?.label ?? "코치"} · ${personality?.description ?? "목표·코칭 대화"}`}
      />
      <AICoachChat variant="full" showRecommendations />
    </div>
  );
}
