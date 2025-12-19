"use client";

import { DownloadButton } from "@/components/common/DownloadButton";

interface DownloadCVButtonProps {
  cvId: string;
  filename: string;
  variant?: "icon" | "button";
}

/**
 * Download CV button for Job Seekers.
 * Wrapper around the common DownloadButton component with CV-specific configuration.
 *
 * Uses Next.js API proxy route to handle authentication (HttpOnly cookies).
 *
 * @param cvId - UUID of the CV to download
 * @param filename - Original filename to use for the download
 * @param variant - 'icon' for compact display (card), 'button' for full button (page header)
 */
export function DownloadCVButton({
  cvId,
  filename,
  variant = "button",
}: DownloadCVButtonProps) {
  // Use Next.js proxy route for same-origin cookie handling
  // This solves the cross-origin HttpOnly cookie issue
  const downloadUrl = `/api/cvs/${cvId}/download`;

  return (
    <DownloadButton
      downloadUrl={downloadUrl}
      filename={filename}
      variant={variant}
      buttonText="Download"
      loadingText="Downloading..."
      successMessage={`Downloaded "${filename}"`}
      testId="download-cv-button"
      errorMessages={{
        401: "Please log in to download",
        403: "You do not have permission to download this CV",
        404: "CV file not found",
      }}
    />
  );
}
