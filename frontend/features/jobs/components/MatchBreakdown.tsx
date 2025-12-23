"use client";

import { useState } from "react";
import { MatchBreakdownResponse } from "@datn/shared-types";
import { SkillBadges } from "./SkillBadges";
import { ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface MatchBreakdownProps {
  breakdown: MatchBreakdownResponse;
}

/**
 * Get experience comparison color based on ratio of actual to required years.
 * - Green: meets or exceeds requirement (ratio >= 1.0)
 * - Yellow: close to requirement (ratio >= 0.7)
 * - Red: significantly below requirement (ratio < 0.7)
 */
function getExperienceColorClass(
  experienceYears: number | null,
  requiredYears: number | null
): string {
  // No color if no experience data or no requirement
  if (experienceYears === null || requiredYears === null || requiredYears === 0) {
    return "text-gray-600";
  }

  const ratio = experienceYears / requiredYears;

  if (ratio >= 1.0) {
    return "text-green-600"; // Meets or exceeds
  } else if (ratio >= 0.7) {
    return "text-yellow-600"; // Close to requirement
  } else {
    return "text-red-600"; // Significantly below
  }
}

/**
 * Format experience display string with comparison to JD requirement.
 */
function formatExperienceDisplay(
  experienceYears: number | null,
  requiredYears: number | null
): string {
  if (experienceYears === null) {
    return "Không xác định";
  }

  if (requiredYears !== null && requiredYears > 0) {
    // Show comparison format: "X/Y năm (yêu cầu Y năm)"
    return `${experienceYears}/${requiredYears} năm (yêu cầu ${requiredYears} năm)`;
  }

  // No requirement, just show years
  return `${experienceYears} năm`;
}

export function MatchBreakdown({ breakdown }: MatchBreakdownProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasMatchedSkills = breakdown.matched_skills.length > 0;
  const hasMissingSkills = breakdown.missing_skills.length > 0;
  const hasExtraSkills = breakdown.extra_skills.length > 0;

  const experienceColorClass = getExperienceColorClass(
    breakdown.experience_years,
    breakdown.required_experience_years
  );

  const experienceDisplay = formatExperienceDisplay(
    breakdown.experience_years,
    breakdown.required_experience_years
  );

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        aria-expanded={isExpanded}
        aria-controls="breakdown-content"
      >
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" aria-hidden="true" />
        ) : (
          <ChevronDown className="h-4 w-4" aria-hidden="true" />
        )}
        <span>Chi tiết đánh giá</span>
      </button>

      {isExpanded && (
        <div id="breakdown-content" className="mt-3 space-y-3 pl-5">
          {/* Matched Skills */}
          {hasMatchedSkills && (
            <div>
              <span className="text-xs font-medium text-gray-500 block mb-1">
                Kỹ năng phù hợp:
              </span>
              <SkillBadges skills={breakdown.matched_skills} type="matched" />
            </div>
          )}

          {/* Missing Skills */}
          {hasMissingSkills && (
            <div>
              <span className="text-xs font-medium text-gray-500 block mb-1">
                Kỹ năng còn thiếu:
              </span>
              <SkillBadges skills={breakdown.missing_skills} type="missing" />
            </div>
          )}

          {/* Extra Skills */}
          {hasExtraSkills && (
            <div>
              <span className="text-xs font-medium text-gray-500 block mb-1">
                Kỹ năng bổ sung:
              </span>
              <SkillBadges skills={breakdown.extra_skills} type="extra" />
            </div>
          )}

          {/* Scores */}
          <div className="flex flex-wrap gap-4 text-sm pt-2 border-t">
            <span className={cn("font-medium", experienceColorClass)}>
              <strong className="text-gray-700">Kinh nghiệm:</strong>{" "}
              {experienceDisplay}
            </span>
            <span className="text-gray-600">
              <strong>Điểm kỹ năng:</strong> {breakdown.skill_score.toFixed(1)}%
            </span>
            <span className="text-gray-600">
              <strong>Điểm kinh nghiệm:</strong> {breakdown.experience_score.toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
