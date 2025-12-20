"use client";

import type { UserStats as UserStatsType } from "@datn/shared-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, TrendingUp, Award, Sparkles, Star } from "lucide-react";

interface UserStatsProps {
  stats: UserStatsType | null;
}

function getScoreColorBg(score: number | null): string {
  if (score === null) return "bg-gray-100 text-gray-600";
  if (score >= 80) return "bg-green-100 text-green-700";
  if (score >= 60) return "bg-yellow-100 text-yellow-700";
  return "bg-red-100 text-red-700";
}

function formatScore(score: number | null): string {
  if (score === null) return "N/A";
  return Math.round(score).toString();
}

export function UserStats({ stats }: UserStatsProps) {
  const hasStats = stats !== null;

  return (
    <Card data-testid="user-stats">
      <CardHeader>
        <CardTitle>Your Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
          {/* Total CVs */}
          <div
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-50"
            data-testid="stat-total-cvs"
          >
            <div className="p-3 rounded-full bg-blue-100">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total CVs</p>
              <p
                className="text-2xl font-bold text-gray-900"
                data-testid="total-cvs-value"
              >
                {hasStats ? stats.total_cvs : 0}
              </p>
            </div>
          </div>

          {/* Average Score */}
          <div
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-50"
            data-testid="stat-average-score"
          >
            <div className={`p-3 rounded-full ${getScoreColorBg(hasStats ? stats.average_score : null)}`}>
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Average Score</p>
              <p
                className="text-2xl font-bold text-gray-900"
                data-testid="average-score-value"
              >
                {hasStats ? formatScore(stats.average_score) : "N/A"}
              </p>
            </div>
          </div>

          {/* Best Score */}
          <div
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-50"
            data-testid="stat-best-score"
          >
            <div className={`p-3 rounded-full ${getScoreColorBg(hasStats ? stats.best_score : null)}`}>
              <Award className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Best Score</p>
              <p
                className="text-2xl font-bold text-gray-900"
                data-testid="best-score-value"
              >
                {hasStats ? formatScore(stats.best_score) : "N/A"}
              </p>
            </div>
          </div>

          {/* Total Unique Skills */}
          <div
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-50"
            data-testid="stat-total-skills"
          >
            <div className="p-3 rounded-full bg-purple-100">
              <Sparkles className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Unique Skills</p>
              <p
                className="text-2xl font-bold text-gray-900"
                data-testid="total-skills-value"
              >
                {hasStats ? stats.total_unique_skills : 0}
              </p>
            </div>
          </div>
        </div>

        {/* Top Skills */}
        {hasStats && stats.top_skills.length > 0 && (
          <div className="mt-6" data-testid="top-skills-section">
            <div className="flex items-center gap-2 mb-3">
              <Star className="h-4 w-4 text-amber-500" />
              <h4 className="text-sm font-medium text-gray-700">Top Skills</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {stats.top_skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                  data-testid={`top-skill-${index}`}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Empty state message */}
        {(!hasStats || stats.total_cvs === 0) && (
          <p
            className="text-center text-gray-500 mt-4"
            data-testid="stats-empty-message"
          >
            Upload your first CV to start tracking your progress!
          </p>
        )}
      </CardContent>
    </Card>
  );
}
