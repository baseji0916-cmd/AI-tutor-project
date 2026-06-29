import type { ReactNode } from "react";
import { Button } from "@/components/ui/Button";

interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  children?: ReactNode;
}

export function EmptyState({ icon, title, description, action, children }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      {icon ? <span className="text-5xl mb-4 opacity-80">{icon}</span> : null}
      <p className="text-base font-medium text-text">{title}</p>
      {description ? (
        <p className="text-sm text-text-muted mt-2 max-w-sm">{description}</p>
      ) : null}
      {action ? (
        <Button className="mt-6" size="sm" onClick={action.onClick}>
          {action.label}
        </Button>
      ) : null}
      {children}
    </div>
  );
}
