import type { CoachPersonality } from "@/types";
import { COACH_PERSONALITY_OPTIONS } from "@/types";
import { cn } from "@/utils/cn";

interface CoachPersonalitySelectProps {
  value: CoachPersonality;
  onChange: (value: CoachPersonality) => void;
}

export function CoachPersonalitySelect({
  value,
  onChange,
}: CoachPersonalitySelectProps) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-text">AI 코치 성격</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {COACH_PERSONALITY_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              "text-left p-3 rounded-xl border transition-all duration-200",
              value === option.value
                ? "border-accent bg-accent/10 ring-1 ring-accent/30"
                : "border-border bg-surface-muted hover:border-accent/40",
            )}
          >
            <span className="block text-sm font-medium text-text">
              {option.label}
            </span>
            <span className="block text-xs text-text-muted mt-0.5">
              {option.description}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
