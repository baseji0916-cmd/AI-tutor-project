interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: string;
  step: string;
}

export function PlaceholderPage({
  title,
  description,
  icon,
  step,
}: PlaceholderPageProps) {
  return (
    <div className="max-w-2xl mx-auto text-center py-16 space-y-4">
      <span className="text-5xl" aria-hidden>
        {icon}
      </span>
      <h1 className="text-2xl font-bold text-text">{title}</h1>
      <p className="text-text-muted">{description}</p>
      <span className="inline-block text-xs px-3 py-1 rounded-full bg-surface-muted border border-border text-text-muted">
        {step}
      </span>
    </div>
  );
}
