"use client";

import { RankedCandidateResponse } from "@datn/shared-types";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { MatchBreakdown } from "./MatchBreakdown";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { FileText } from "lucide-react";

interface CandidateCardProps {
  candidate: RankedCandidateResponse;
  rank: number;
}

export function CandidateCard({ candidate, rank }: CandidateCardProps) {
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
            </h3>
            {candidate.cv_summary && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                {candidate.cv_summary}
              </p>
            )}
          </div>
        </div>

        {/* Right: Score Badge */}
        <div className="shrink-0 self-start sm:self-center">
          <MatchScoreBadge score={candidate.match_score} size="md" />
        </div>
      </div>

      {/* Match Breakdown */}
      <MatchBreakdown breakdown={candidate.breakdown} />

      {/* Actions */}
      <div className="mt-4 flex justify-end pt-3 border-t">
        <Link href={`/cvs/${candidate.cv_id}`}>
          <Button variant="outline" size="sm">
            Xem CV
          </Button>
        </Link>
      </div>
    </Card>
  );
}
