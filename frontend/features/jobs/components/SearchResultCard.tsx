"use client";

import Link from "next/link";
import { SearchResultResponse } from "@datn/shared-types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { SkillBadges } from "./SkillBadges";
import { FileText, Eye } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SearchResultCardProps {
  result: SearchResultResponse;
  rank: number;
}

export function SearchResultCard({ result, rank }: SearchResultCardProps) {
  const displayFilename = result.filename || `CV #${result.cv_id.slice(0, 8)}`;
  const truncatedSummary = result.cv_summary
    ? result.cv_summary.length > 150
      ? result.cv_summary.slice(0, 150) + "..."
      : result.cv_summary
    : "Khong co mo ta";

  return (
    <Card
      className={cn(
        "transition-all duration-200 hover:shadow-md hover:border-primary/50",
        "group"
      )}
      role="listitem"
      aria-label={`Ung vien ${rank}: ${displayFilename}, diem ${result.relevance_score}%`}
    >
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Rank and Score */}
          <div className="flex sm:flex-col items-center sm:items-start gap-3 sm:gap-2">
            <span className="text-lg font-bold text-muted-foreground">
              #{rank}
            </span>
            <MatchScoreBadge score={result.relevance_score} size="md" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-2">
            {/* Filename */}
            <div className="flex items-center gap-2">
              <FileText
                className="h-4 w-4 text-muted-foreground shrink-0"
                aria-hidden="true"
              />
              <span className="font-medium truncate">{displayFilename}</span>
            </div>

            {/* Summary */}
            <p className="text-sm text-muted-foreground line-clamp-2">
              {truncatedSummary}
            </p>

            {/* Matched Skills */}
            {result.matched_skills.length > 0 && (
              <div className="pt-1">
                <SkillBadges
                  skills={result.matched_skills}
                  type="matched"
                  maxDisplay={4}
                />
              </div>
            )}
          </div>

          {/* Action Button */}
          <div className="flex sm:flex-col justify-end sm:justify-center">
            <Button asChild variant="outline" size="sm">
              <Link
                href={`/jobs/candidates/${result.cv_id}`}
                aria-label={`Xem CV cua ${displayFilename}`}
              >
                <Eye className="h-4 w-4 mr-1" />
                Xem CV
              </Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
