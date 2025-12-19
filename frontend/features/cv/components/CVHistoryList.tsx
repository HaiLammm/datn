"use client";

import { CVWithStatus } from "@datn/shared-types";
import Link from "next/link";
import { CVHistoryCard } from "./CVHistoryCard";
import {
  useDeleteMode,
} from "@/features/cv/context/DeleteModeContext";
import { Button } from "@/components/ui/button";

interface CVHistoryListProps {
  cvs: CVWithStatus[];
}

/**
 * Empty state component shown when user has no CVs uploaded.
 */
function EmptyState() {
  return (
    <div className="text-center py-12" data-testid="cv-empty-state">
      <div className="text-gray-400 mb-4">
        <svg
          className="mx-auto h-12 w-12"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        No CVs uploaded yet
      </h3>
      <p className="text-gray-600 mb-6">
        Get started by uploading your first CV for analysis.
      </p>
      <Link
        href="/cvs/upload"
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        data-testid="upload-first-cv-link"
      >
        Upload Your First CV
      </Link>
    </div>
  );
}

/**
 * CV History List component that displays all user CVs in a responsive grid.
 * Shows empty state when no CVs are present.
 * Includes delete mode notification banner.
 */
export function CVHistoryList({ cvs }: CVHistoryListProps) {
  const { skipConfirmation, resetConfirmation } = useDeleteMode();

  if (cvs.length === 0) {
    return <EmptyState />;
  }

  return (
    <>
      {/* CV Count Header */}
      <div className="mb-4">
        <p className="text-sm text-gray-600" data-testid="cv-count">
          Your CVs ({cvs.length} total)
        </p>
      </div>

      {/* Delete Mode Warning Banner */}
      {skipConfirmation && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md flex items-center justify-between">
          <p className="text-sm text-yellow-800">
            Quick delete mode is enabled. CVs will be deleted without
            confirmation.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={resetConfirmation}
            className="ml-4 shrink-0"
          >
            Enable Confirmation
          </Button>
        </div>
      )}

      {/* CV Cards Grid */}
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3" data-testid="cv-grid">
        {cvs.map((cv) => (
          <CVHistoryCard key={cv.id} cv={cv} />
        ))}
      </div>
    </>
  );
}

// Export EmptyState for testing
export { EmptyState };
