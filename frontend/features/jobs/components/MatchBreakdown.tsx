"use client";

import { useState } from "react";
import { MatchBreakdownResponse } from "@datn/shared-types";
import { SkillBadges } from "./SkillBadges";
import { ChevronDown, ChevronUp } from "lucide-react";

interface MatchBreakdownProps {
  breakdown: MatchBreakdownResponse;
}

export function MatchBreakdown({ breakdown }: MatchBreakdownProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasMatchedSkills = breakdown.matched_skills.length > 0;
  const hasMissingSkills = breakdown.missing_skills.length > 0;
  const hasExtraSkills = breakdown.extra_skills.length > 0;

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
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 pt-2 border-t">
            <span>
              <strong>Kinh nghiệm:</strong>{" "}
              {breakdown.experience_years !== null
                ? `${breakdown.experience_years} năm`
                : "Không xác định"}
            </span>
            <span>
              <strong>Điểm kỹ năng:</strong> {breakdown.skill_score}/70
            </span>
            <span>
              <strong>Điểm kinh nghiệm:</strong> {breakdown.experience_score}/30
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
