"use client";

import { RankedCandidateResponse } from "@datn/shared-types";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { MatchBreakdown } from "./MatchBreakdown";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { FileText, Eye, Lock, Loader2 } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface CandidateCardProps {
  candidate: RankedCandidateResponse;
  rank: number;
  jdId: string;
  /** Story 5.7: Job match score (0-100), undefined if not yet calculated */
  jobMatchScore?: number | null;
  /** Story 5.7: Whether job match score is being loaded */
  isLoadingJobMatchScore?: boolean;
}

/**
 * Get color class for job match score badge
 * Story 5.7: Green >= 70, Yellow 40-69, Red < 40
 */
function getJobMatchScoreColor(score: number): string {
  if (score >= 70) return "bg-green-100 text-green-800 border-green-200";
  if (score >= 40) return "bg-yellow-100 text-yellow-800 border-yellow-200";
  return "bg-red-100 text-red-800 border-red-200";
}

export function CandidateCard({
  candidate,
  rank,
  jdId,
  jobMatchScore,
  isLoadingJobMatchScore,
}: CandidateCardProps) {
  const displayName =
    candidate.filename || `CV #${candidate.cv_id.slice(0, 8)}`;

  return (
    <Card
      className="p-4 hover:shadow-md transition-shadow"
      role="article"
      aria-label={`Candidate rank ${rank}: ${displayName}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        {/* Left: Rank and Info */}
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span
            className="text-2xl font-bold text-muted-foreground shrink-0"
            aria-label={`Rank ${rank}`}
          >
            #{rank}
          </span>
          <div className="min-w-0 flex-1">
            <h3 className="font-medium text-gray-900 truncate flex items-center gap-2">
              <FileText className="h-4 w-4 text-gray-400 shrink-0" aria-hidden="true" />
              {displayName}
              {/* Visibility Indicator */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ml-2 ${
                        candidate.is_public
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {candidate.is_public ? (
                        <>
                          <Eye className="h-3 w-3 mr-1" aria-hidden="true" />
                          Public
                        </>
                      ) : (
                        <>
                          <Lock className="h-3 w-3 mr-1" aria-hidden="true" />
                          Private
                        </>
                      )}
                    </span>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>
                      {candidate.is_public
                        ? "Full CV details available"
                        : "CV is private. Match details visible only."}
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </h3>
            {candidate.cv_summary && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                {candidate.cv_summary}
              </p>
            )}
          </div>
        </div>

        {/* Right: Score Badges */}
        <div className="shrink-0 self-start sm:self-center flex flex-col items-end gap-2">
          {/* Original Match Score Badge - Secondary */}
          <MatchScoreBadge score={candidate.match_score} size="sm" />
        </div>
      </div>

      {/* Match Breakdown */}
      <MatchBreakdown breakdown={candidate.breakdown} />

      {/* Actions */}
      <div className="mt-4 flex justify-end pt-3 border-t">
        {candidate.is_public ? (
          <Link href={`/jobs/jd/${jdId}/candidates/${candidate.cv_id}`}>
            <Button variant="outline" size="sm">
              Xem CV
            </Button>
          </Link>
        ) : (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="sm" disabled className="opacity-50">
                  <Lock className="h-4 w-4 mr-2" />
                  CV Private
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>This candidate&apos;s CV is private. They may choose to make it public in the future.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
    </Card>
  );
}
