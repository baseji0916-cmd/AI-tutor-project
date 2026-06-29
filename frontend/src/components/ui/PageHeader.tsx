import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

/** Apple-style page title block */
export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-4 mb-2">
      <div>
        <h1 className="text-[1.75rem] font-semibold tracking-tight text-text leading-tight">
          {title}
        </h1>
        {subtitle ? (
          <p className="text-[15px] text-text-muted mt-1 leading-snug">{subtitle}</p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
