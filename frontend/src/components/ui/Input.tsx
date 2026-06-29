import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s/g, "-");

    return (
      <div className="space-y-1.5">
        {label ? (
          <label htmlFor={inputId} className="block text-sm font-medium text-text">
            {label}
          </label>
        ) : null}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "w-full h-11 px-4 rounded-xl",
            "bg-surface-muted border border-border",
            "text-text placeholder:text-text-muted",
            "focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent",
            "transition-all duration-200",
            error && "border-red-500 focus:ring-red-500/40",
            className,
          )}
          {...props}
        />
        {error ? <p className="text-xs text-red-500">{error}</p> : null}
      </div>
    );
  },
);

Input.displayName = "Input";
