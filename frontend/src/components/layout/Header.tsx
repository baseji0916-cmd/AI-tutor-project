import { Link } from "react-router-dom";
import { useAuth } from "@/stores/AuthContext";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { COACH_PERSONALITY_OPTIONS } from "@/types";

export function Header() {
  const { user } = useAuth();

  const personalityLabel = COACH_PERSONALITY_OPTIONS.find(
    (p) => p.value === user?.coach_personality,
  )?.label;

  return (
    <header className="sticky top-0 z-40 flex h-[52px] items-center justify-between gap-4 border-b border-border/60 bg-surface/75 backdrop-blur-2xl px-4 lg:px-5">
      <div className="lg:hidden">
        <span className="text-[17px] font-semibold tracking-tight text-text">
          Growth<span className="text-accent">Pilot</span>
        </span>
      </div>

      <div className="hidden lg:block min-w-0">
        <p className="text-sm text-text-muted truncate">
          <span className="font-medium text-text">
            {user?.full_name ?? user?.username}
          </span>
          {personalityLabel ? (
            <span className="ml-2 text-[11px] px-2 py-0.5 rounded-full bg-surface-muted border border-border/60">
              {personalityLabel}
            </span>
          ) : null}
        </p>
      </div>

      <div className="flex items-center gap-1 ml-auto">
        <ThemeToggle />
        <Link
          to="/settings"
          className="p-2 rounded-xl text-text-muted hover:text-text hover:bg-surface-muted transition-colors text-sm"
          aria-label="설정"
        >
          ⚙
        </Link>
      </div>
    </header>
  );
}
