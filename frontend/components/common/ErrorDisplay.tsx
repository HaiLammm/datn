"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorDisplayProps {
  /** Error message to display */
  message: string;
  /** Title for the error (optional) */
  title?: string;
  /** Callback for retry button */
  onRetry?: () => void;
  /** Text for retry button */
  retryText?: string;
  /** Whether retry is in progress */
  isRetrying?: boolean;
  /** Variant: 'inline' for small messages, 'card' for larger display */
  variant?: "inline" | "card";
  /** Additional CSS classes */
  className?: string;
}

/**
 * Reusable error display component with optional retry functionality.
 * Use for failed API calls, upload errors, and other recoverable errors.
 *
 * @example
 * // Inline error with retry
 * <ErrorDisplay
 *   message="Failed to load data"
 *   onRetry={handleRetry}
 * />
 *
 * @example
 * // Card variant for prominent errors
 * <ErrorDisplay
 *   variant="card"
 *   title="Upload Failed"
 *   message="The file could not be uploaded. Please try again."
 *   onRetry={handleRetry}
 *   retryText="Try Again"
 * />
 */
export function ErrorDisplay({
  message,
  title,
  onRetry,
  retryText = "Retry",
  isRetrying = false,
  variant = "inline",
  className,
}: ErrorDisplayProps) {
  if (variant === "card") {
    return (
      <div
        className={cn(
          "p-6 bg-red-50 border border-red-200 rounded-lg",
          className
        )}
        data-testid="error-display"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            {title && (
              <h3 className="text-lg font-medium text-red-800 mb-1">{title}</h3>
            )}
            <p className="text-red-700">{message}</p>
            {onRetry && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onRetry}
                disabled={isRetrying}
                className="mt-4 text-red-700 border-red-300 hover:bg-red-100"
                data-testid="error-retry-button"
              >
                <RefreshCw
                  className={cn(
                    "h-4 w-4 mr-2",
                    isRetrying && "animate-spin"
                  )}
                />
                {isRetrying ? "Retrying..." : retryText}
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "p-3 bg-red-50 border border-red-200 rounded-md flex items-center gap-2",
        className
      )}
      data-testid="error-display"
    >
      <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />
      <span className="text-red-700 text-sm flex-1">{message}</span>
      {onRetry && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onRetry}
          disabled={isRetrying}
          className="text-red-700 hover:text-red-800 hover:bg-red-100 shrink-0 h-7 px-2"
          data-testid="error-retry-button"
        >
          <RefreshCw
            className={cn(
              "h-3 w-3",
              isRetrying && "animate-spin"
            )}
          />
          <span className="ml-1 text-xs">{isRetrying ? "..." : retryText}</span>
        </Button>
      )}
    </div>
  );
}
