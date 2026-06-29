import { cn } from "@/utils/cn";

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent",
        className,
      )}
      role="status"
      aria-label="로딩 중"
    />
  );
}
