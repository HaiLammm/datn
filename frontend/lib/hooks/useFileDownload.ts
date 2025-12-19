"use client";

import { useState, useCallback } from "react";

export interface DownloadOptions {
  /** URL to fetch the file from */
  url: string;
  /** Filename to use when saving (fallback if not provided by server) */
  filename: string;
  /** Optional callback on success */
  onSuccess?: () => void;
  /** Optional callback on error with status code and message */
  onError?: (status: number, message: string) => void;
}

export interface UseFileDownloadReturn {
  /** Whether a download is in progress */
  isDownloading: boolean;
  /** Error message if download failed */
  error: string | null;
  /** Trigger the download */
  download: (options: DownloadOptions) => Promise<void>;
  /** Clear the error state */
  clearError: () => void;
}

/**
 * Custom hook for handling file downloads with proper error handling.
 * Extracts common download logic used across Job Seeker and Recruiter flows.
 *
 * @example
 * ```tsx
 * const { isDownloading, error, download } = useFileDownload();
 *
 * const handleDownload = () => {
 *   download({
 *     url: `/api/v1/cvs/${cvId}/download`,
 *     filename: 'my-resume.pdf',
 *     onSuccess: () => toast.success('Downloaded!'),
 *     onError: (status, msg) => toast.error(msg),
 *   });
 * };
 * ```
 */
export function useFileDownload(): UseFileDownloadReturn {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const download = useCallback(async (options: DownloadOptions): Promise<void> => {
    const { url, filename, onSuccess, onError } = options;

    setIsDownloading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        method: "GET",
        credentials: "include",
      });

      if (!response.ok) {
        let errorMessage = "Failed to download file";
        const status = response.status;

        switch (status) {
          case 401:
            errorMessage = "Please log in to download";
            break;
          case 403:
            errorMessage = "You do not have permission to download this file";
            break;
          case 404:
            errorMessage = "File not found";
            break;
          default:
            errorMessage = `Download failed (HTTP ${status})`;
        }

        setError(errorMessage);
        onError?.(status, errorMessage);
        return;
      }

      // Extract filename from Content-Disposition header if available
      const contentDisposition = response.headers.get("content-disposition");
      let downloadFilename = filename;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
        if (filenameMatch) {
          downloadFilename = filenameMatch[1];
        }
      }

      // Create blob from response and trigger download
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = downloadFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      onSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to download file";
      setError(errorMessage);
      onError?.(0, errorMessage);
    } finally {
      setIsDownloading(false);
    }
  }, []);

  return {
    isDownloading,
    error,
    download,
    clearError,
  };
}
