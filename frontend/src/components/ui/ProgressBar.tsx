import { cn } from "@/utils/cn";

interface ProgressBarProps {
  value: number;
  className?: string;
  label?: string;
  showValue?: boolean;
}

export function ProgressBar({
  value,
  className,
  label,
  showValue = true,
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={cn("space-y-1.5", className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between text-xs">
          {label ? <span className="text-text-muted truncate pr-2">{label}</span> : <span />}
          {showValue ? (
            <span className="text-text font-medium tabular-nums shrink-0">
              {Math.round(clamped)}%
            </span>
          ) : null}
        </div>
      )}
      <div className="h-2 rounded-full bg-surface-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-accent transition-all duration-500 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
