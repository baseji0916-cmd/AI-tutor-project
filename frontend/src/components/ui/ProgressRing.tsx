import { cn } from "@/utils/cn";

interface ProgressRingProps {
  value: number;
  size?: number;
  stroke?: number;
  className?: string;
  label?: string;
}

/** Circular progress indicator — Apple Fitness style */
export function ProgressRing({
  value,
  size = 88,
  stroke = 8,
  className,
  label,
}: ProgressRingProps) {
  const clamped = Math.min(100, Math.max(0, value));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (clamped / 100) * c;

  return (
    <div className={cn("relative inline-flex flex-col items-center", className)}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          className="text-surface-muted"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className="text-accent transition-all duration-700 ease-out"
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-lg font-semibold text-text">
        {Math.round(clamped)}%
      </span>
      {label ? (
        <span className="text-xs text-text-muted mt-2 text-center">{label}</span>
      ) : null}
    </div>
  );
}
