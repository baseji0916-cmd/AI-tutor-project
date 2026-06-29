import type { ReactNode } from "react";
import { cn } from "@/utils/cn";

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}

export function Card({ children, className, title, subtitle }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-border bg-surface-elevated p-5",
        "shadow-sm transition-shadow hover:shadow-md",
        className,
      )}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title ? (
            <h3 className="text-base font-semibold text-text">{title}</h3>
          ) : null}
          {subtitle ? (
            <p className="text-sm text-text-muted mt-0.5">{subtitle}</p>
          ) : null}
        </div>
      )}
      {children}
    </div>
  );
}
