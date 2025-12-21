"use client";

import { useState, useCallback } from "react";

export interface UploadState {
  /** Whether upload is in progress */
  isUploading: boolean;
  /** Upload progress percentage (0-100) */
  progress: number;
  /** Error message if upload failed */
  error: string | null;
  /** Whether upload completed successfully */
  isSuccess: boolean;
}

export interface UploadOptions {
  /** File to upload */
  file: File;
  /** Upload endpoint URL */
  url: string;
  /** Field name for the file in FormData */
  fieldName?: string;
  /** Additional form data fields */
  additionalData?: Record<string, string>;
  /** Callback on successful upload */
  onSuccess?: (response: unknown) => void;
  /** Callback on upload error */
  onError?: (error: string) => void;
  /** Callback on progress update */
  onProgress?: (progress: number) => void;
}

export interface UseFileUploadReturn extends UploadState {
  /** Start file upload */
  upload: (options: UploadOptions) => Promise<void>;
  /** Reset state to initial */
  reset: () => void;
}

const initialState: UploadState = {
  isUploading: false,
  progress: 0,
  error: null,
  isSuccess: false,
};

/**
 * Custom hook for file uploads with progress tracking.
 * Uses XMLHttpRequest to track upload progress.
 *
 * @example
 * ```tsx
 * const { isUploading, progress, error, upload } = useFileUpload();
 *
 * const handleUpload = async (file: File) => {
 *   await upload({
 *     file,
 *     url: '/api/cvs',
 *     fieldName: 'file',
 *     onSuccess: () => toast.success('Uploaded!'),
 *     onError: (err) => toast.error(err),
 *   });
 * };
 * ```
 */
export function useFileUpload(): UseFileUploadReturn {
  const [state, setState] = useState<UploadState>(initialState);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  const upload = useCallback(async (options: UploadOptions): Promise<void> => {
    const {
      file,
      url,
      fieldName = "file",
      additionalData,
      onSuccess,
      onError,
      onProgress,
    } = options;

    setState({
      isUploading: true,
      progress: 0,
      error: null,
      isSuccess: false,
    });

    return new Promise((resolve) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();

      formData.append(fieldName, file);

      // Add any additional form data
      if (additionalData) {
        Object.entries(additionalData).forEach(([key, value]) => {
          formData.append(key, value);
        });
      }

      // Track upload progress
      xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          setState((prev) => ({ ...prev, progress: percentComplete }));
          onProgress?.(percentComplete);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          let response: unknown;
          try {
            response = JSON.parse(xhr.responseText);
          } catch {
            response = xhr.responseText;
          }
          setState({
            isUploading: false,
            progress: 100,
            error: null,
            isSuccess: true,
          });
          onSuccess?.(response);
        } else {
          let errorMessage = "Upload failed";
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            errorMessage = errorResponse.detail || errorResponse.message || errorMessage;
          } catch {
            if (xhr.status === 401) errorMessage = "Please log in to upload";
            else if (xhr.status === 413) errorMessage = "File is too large";
            else if (xhr.status === 415) errorMessage = "File type not supported";
            else errorMessage = `Upload failed (HTTP ${xhr.status})`;
          }
          setState({
            isUploading: false,
            progress: 0,
            error: errorMessage,
            isSuccess: false,
          });
          onError?.(errorMessage);
        }
        resolve();
      });

      xhr.addEventListener("error", () => {
        const errorMessage = "Network error. Please check your connection.";
        setState({
          isUploading: false,
          progress: 0,
          error: errorMessage,
          isSuccess: false,
        });
        onError?.(errorMessage);
        resolve();
      });

      xhr.addEventListener("abort", () => {
        setState({
          isUploading: false,
          progress: 0,
          error: "Upload cancelled",
          isSuccess: false,
        });
        resolve();
      });

      xhr.open("POST", url);
      xhr.withCredentials = true; // Include cookies for authentication
      xhr.send(formData);
    });
  }, []);

  return {
    ...state,
    upload,
    reset,
  };
}
