import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  /** Size of the spinner: 'sm' (16px), 'md' (24px), 'lg' (32px), 'xl' (48px) */
  size?: "sm" | "md" | "lg" | "xl";
  /** Optional message to display below spinner */
  message?: string;
  /** Additional CSS classes */
  className?: string;
  /** Whether to center the spinner in its container */
  centered?: boolean;
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
  xl: "h-12 w-12",
};

/**
 * Generic loading spinner component for async operations.
 * Use this for buttons, forms, and inline loading states.
 *
 * @example
 * // In a button
 * <Button disabled={isPending}>
 *   {isPending && <LoadingSpinner size="sm" className="mr-2" />}
 *   {isPending ? "Saving..." : "Save"}
 * </Button>
 *
 * @example
 * // Centered in container
 * <LoadingSpinner size="lg" message="Loading data..." centered />
 */
export function LoadingSpinner({
  size = "md",
  message,
  className,
  centered = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <div
      className={cn(
        "inline-flex flex-col items-center gap-2",
        centered && "absolute inset-0 flex items-center justify-center",
        className
      )}
    >
      <Loader2
        className={cn("animate-spin text-primary", sizeClasses[size])}
        data-testid="loading-spinner"
      />
      {message && (
        <span className="text-sm text-muted-foreground">{message}</span>
      )}
    </div>
  );

  if (centered) {
    return <div className="relative min-h-[100px]">{spinner}</div>;
  }

  return spinner;
}
