"use client";

import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useFileDownload } from "@/lib/hooks/useFileDownload";
import { toast } from "sonner";

export interface DownloadButtonProps {
  /** URL to download the file from */
  downloadUrl: string;
  /** Filename to use for the downloaded file */
  filename: string;
  /** Visual variant: 'icon' for icon-only, 'button' for full button with text */
  variant?: "icon" | "button";
  /** Button size */
  size?: "sm" | "default" | "lg";
  /** Custom button text (only used with 'button' variant) */
  buttonText?: string;
  /** Custom loading text (only used with 'button' variant) */
  loadingText?: string;
  /** Custom success message for toast */
  successMessage?: string;
  /** Custom class name */
  className?: string;
  /** Test ID for testing */
  testId?: string;
  /** Custom error messages by HTTP status code */
  errorMessages?: {
    401?: string;
    403?: string;
    404?: string;
    default?: string;
  };
}

/**
 * Reusable download button component.
 * Supports both icon-only and full button variants.
 * Handles loading state, error handling with toast notifications.
 *
 * @example
 * ```tsx
 * // Icon variant (compact)
 * <DownloadButton
 *   downloadUrl={`/api/v1/cvs/${cvId}/download`}
 *   filename="resume.pdf"
 *   variant="icon"
 * />
 *
 * // Button variant (with text)
 * <DownloadButton
 *   downloadUrl={`/api/jobs/candidates/${cvId}/file?download=true`}
 *   filename="candidate-cv.pdf"
 *   variant="button"
 *   buttonText="Tải xuống"
 * />
 * ```
 */
export function DownloadButton({
  downloadUrl,
  filename,
  variant = "icon",
  size = "sm",
  buttonText = "Download",
  loadingText = "...",
  successMessage = "File downloaded successfully",
  className = "",
  testId = "download-button",
  errorMessages = {},
}: DownloadButtonProps) {
  const { isDownloading, download } = useFileDownload();

  const handleDownload = async () => {
    await download({
      url: downloadUrl,
      filename,
      onSuccess: () => {
        if (successMessage) {
          toast.success(successMessage);
        }
      },
      onError: (status, defaultMessage) => {
        let message = defaultMessage;
        switch (status) {
          case 401:
            message = errorMessages[401] || "Please log in to download";
            break;
          case 403:
            message = errorMessages[403] || "You do not have permission to download this file";
            break;
          case 404:
            message = errorMessages[404] || "File not found";
            break;
          default:
            message = errorMessages.default || defaultMessage;
        }
        toast.error(message);
      },
    });
  };

  if (variant === "icon") {
    return (
      <Button
        variant="outline"
        size="icon"
        onClick={handleDownload}
        disabled={isDownloading}
        className={className}
        data-testid={testId}
        title={buttonText}
      >
        {isDownloading ? (
          <Loader2 className="h-4 w-4 animate-spin" data-testid={`${testId}-loading`} />
        ) : (
          <Download className="h-4 w-4" />
        )}
      </Button>
    );
  }

  return (
    <Button
      variant="outline"
      size={size}
      onClick={handleDownload}
      disabled={isDownloading}
      className={`flex items-center gap-1 ${className}`}
      data-testid={testId}
    >
      {isDownloading ? (
        <Loader2 className="h-4 w-4 animate-spin" data-testid={`${testId}-loading`} />
      ) : (
        <Download className="h-4 w-4" />
      )}
      {isDownloading ? loadingText : buttonText}
    </Button>
  );
}
