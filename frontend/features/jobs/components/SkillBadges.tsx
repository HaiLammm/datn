"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";

interface SkillBadgesProps {
  skills: string[];
  type: "matched" | "missing" | "extra";
  maxDisplay?: number;
}

function getTypeClasses(type: "matched" | "missing" | "extra"): string {
  switch (type) {
    case "matched":
      return "bg-green-100 text-green-800";
    case "missing":
      return "bg-red-100 text-red-800";
    case "extra":
      return "bg-gray-100 text-gray-800";
  }
}

function getTypeLabel(type: "matched" | "missing" | "extra"): string {
  switch (type) {
    case "matched":
      return "Matched skills";
    case "missing":
      return "Missing skills";
    case "extra":
      return "Extra skills";
  }
}

export function SkillBadges({ skills, type, maxDisplay = 4 }: SkillBadgesProps) {
  const [showAll, setShowAll] = useState(false);
  const typeClasses = getTypeClasses(type);
  const typeLabel = getTypeLabel(type);

  if (skills.length === 0) {
    return null;
  }

  const displayedSkills = showAll ? skills : skills.slice(0, maxDisplay);
  const remainingCount = skills.length - maxDisplay;

  return (
    <div
      role="list"
      aria-label={typeLabel}
      className="flex flex-wrap gap-1.5"
    >
      {displayedSkills.map((skill, index) => (
        <span
          key={`${skill}-${index}`}
          role="listitem"
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
            typeClasses
          )}
        >
          {skill}
        </span>
      ))}
      {!showAll && remainingCount > 0 && (
        <button
          onClick={() => setShowAll(true)}
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium cursor-pointer hover:opacity-80",
            typeClasses
          )}
          title={`Show ${remainingCount} more ${type} skills`}
          aria-label={`Show ${remainingCount} more ${type} skills`}
        >
          +{remainingCount} more
        </button>
      )}
      {showAll && skills.length > maxDisplay && (
        <button
          onClick={() => setShowAll(false)}
          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium text-gray-500 hover:text-gray-700"
          aria-label="Show less"
        >
          Show less
        </button>
      )}
    </div>
  );
}
