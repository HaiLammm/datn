"use client";

import { cn } from "@/lib/utils";

interface MatchScoreBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

function getScoreColor(score: number): string {
  if (score >= 70) return "bg-green-500 text-white";
  if (score >= 50) return "bg-yellow-500 text-white";
  return "bg-red-500 text-white";
}

function getSizeClasses(size: "sm" | "md" | "lg"): string {
  switch (size) {
    case "sm":
      return "h-8 w-8 text-xs";
    case "lg":
      return "h-14 w-14 text-lg";
    case "md":
    default:
      return "h-10 w-10 text-sm";
  }
}

export function MatchScoreBadge({ score, size = "md" }: MatchScoreBadgeProps) {
  const colorClasses = getScoreColor(score);
  const sizeClasses = getSizeClasses(size);

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-full font-bold",
        colorClasses,
        sizeClasses
      )}
      aria-label={`Match score: ${score}%`}
      role="img"
    >
      {score}%
    </div>
  );
}
