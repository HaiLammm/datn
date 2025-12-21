"use client";

import { CVWithStatus } from "@datn/shared-types";
import { CVHistoryCard } from "./CVHistoryCard";
import { NoCVsYet } from "./NoCVsYet";
import {
  useDeleteMode,
} from "@/features/cv/context/DeleteModeContext";
import { Button } from "@/components/ui/button";

interface CVHistoryListProps {
  cvs: CVWithStatus[];
}

/**
 * CV History List component that displays all user CVs in a responsive grid.
 * Shows empty state when no CVs are present.
 * Includes delete mode notification banner.
 */
export function CVHistoryList({ cvs }: CVHistoryListProps) {
  const { skipConfirmation, resetConfirmation } = useDeleteMode();

  if (cvs.length === 0) {
    return <NoCVsYet />;
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
