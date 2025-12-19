"use client";

import { CVWithStatus } from "@datn/shared-types";
import Link from "next/link";
import { DeleteCVDialog } from "@/features/cv/components/DeleteCVDialog";
import { CVVisibilityToggle } from "@/features/cv/components/CVVisibilityToggle";
import { DownloadCVButton } from "@/features/cv/components/DownloadCVButton";

interface CVHistoryCardProps {
  cv: CVWithStatus;
}

/**
 * Returns the appropriate color class for a quality score.
 * - Green (80-100): text-green-600
 * - Yellow (60-79): text-yellow-600
 * - Red (0-59): text-red-600
 * - Gray (null/pending): text-gray-500
 */
function getScoreColor(score: number | null): string {
  if (score === null) return "text-gray-500";
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

/**
 * Returns display text for quality score based on score value and analysis status.
 */
function getScoreDisplay(
  score: number | null,
  status: CVWithStatus["analysis_status"]
): string {
  if (score === null) {
    if (status === "PENDING" || status === "PROCESSING") {
      return "Analyzing...";
    }
    return "N/A";
  }
  return `${score}/100`;
}

/**
 * Formats date to readable format: "Dec 15, 2025"
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Returns the status badge component for analysis status.
 */
function getStatusBadge(status: CVWithStatus["analysis_status"]) {
  switch (status) {
    case "COMPLETED":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Completed
        </span>
      );
    case "PROCESSING":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Processing
        </span>
      );
    case "FAILED":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          Failed
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          Pending
        </span>
      );
  }
}

export function CVHistoryCard({ cv }: CVHistoryCardProps) {
  const scoreColor = getScoreColor(cv.quality_score);
  const scoreDisplay = getScoreDisplay(cv.quality_score, cv.analysis_status);

  return (
    <div className="bg-white rounded-lg shadow p-6" data-testid="cv-history-card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {cv.filename}
          </h3>
          <p className="text-sm text-gray-600">
            Uploaded {formatDate(cv.uploaded_at)}
          </p>
        </div>
        {getStatusBadge(cv.analysis_status)}
      </div>

      {/* Quality Score */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Quality Score</span>
          <span className={`text-lg font-semibold ${scoreColor}`} data-testid="quality-score">
            {scoreDisplay}
          </span>
        </div>
      </div>

      {/* Visibility Toggle */}
      <div className="mb-4 py-3 border-t border-b border-gray-100">
        <CVVisibilityToggle cvId={cv.id} isPublic={cv.is_public} />
      </div>

      <div className="flex space-x-3">
        <Link
          href={`/cvs/${cv.id}/analysis`}
          className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          data-testid="view-analysis-link"
        >
          View Analysis
        </Link>
        <DownloadCVButton cvId={cv.id} filename={cv.filename} variant="icon" />
        <DeleteCVDialog cvId={cv.id} filename={cv.filename} />
      </div>
    </div>
  );
}

// Export utility functions for testing
export { getScoreColor, getScoreDisplay, formatDate };
