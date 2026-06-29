import { Link } from "react-router-dom";
import { mobileMoreNav } from "@/config/navigation";
import { PageHeader } from "@/components/ui/PageHeader";

/** Mobile overflow menu — Apple Settings list style */
export function MorePage() {
  return (
    <div className="space-y-6 max-w-lg mx-auto">
      <PageHeader title="더보기" subtitle="추가 기능 및 설정" />
      <div className="rounded-2xl border border-border/60 bg-surface-elevated overflow-hidden divide-y divide-border/60">
        {mobileMoreNav.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className="flex items-center gap-4 px-4 py-3.5 hover:bg-surface-muted/50 transition-colors active:bg-surface-muted"
          >
            <span className="w-8 h-8 rounded-xl bg-surface-muted flex items-center justify-center text-lg">
              {item.icon}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-[15px] font-medium text-text">{item.label}</p>
              {item.description ? (
                <p className="text-xs text-text-muted truncate">{item.description}</p>
              ) : null}
            </div>
            <span className="text-text-muted text-sm">›</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
