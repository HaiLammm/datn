"use client";

import { CVWithStatus } from "@datn/shared-types";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, TrendingUp, Award } from "lucide-react";

interface DashboardStatsProps {
  cvs: CVWithStatus[];
}

interface StatsData {
  totalCvs: number;
  averageScore: number | null;
  bestScore: number | null;
}

function calculateStats(cvs: CVWithStatus[]): StatsData {
  const completedCvs = cvs.filter((cv) => cv.quality_score !== null);
  const scores = completedCvs.map((cv) => cv.quality_score!);

  return {
    totalCvs: cvs.length,
    averageScore:
      scores.length > 0
        ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
        : null,
    bestScore: scores.length > 0 ? Math.max(...scores) : null,
  };
}

function getScoreColorBg(score: number | null): string {
  if (score === null) return "bg-gray-100 text-gray-600";
  if (score >= 80) return "bg-green-100 text-green-700";
  if (score >= 60) return "bg-yellow-100 text-yellow-700";
  return "bg-red-100 text-red-700";
}

export function DashboardStats({ cvs }: DashboardStatsProps) {
  const stats = calculateStats(cvs);
  const hasScores = stats.averageScore !== null;

  return (
    <div data-testid="dashboard-stats">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Stats</h3>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3">
        {/* Total CVs */}
        <Card data-testid="stat-total-cvs">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-blue-100">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total CVs</p>
                <p className="text-2xl font-bold text-gray-900" data-testid="total-cvs-value">
                  {stats.totalCvs}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Average Score */}
        <Card data-testid="stat-average-score">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-full ${getScoreColorBg(stats.averageScore)}`}>
                <TrendingUp className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Average Score</p>
                <p
                  className="text-2xl font-bold text-gray-900"
                  data-testid="average-score-value"
                >
                  {hasScores ? stats.averageScore : "N/A"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Best Score */}
        <Card data-testid="stat-best-score">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-full ${getScoreColorBg(stats.bestScore)}`}>
                <Award className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Best Score</p>
                <p
                  className="text-2xl font-bold text-gray-900"
                  data-testid="best-score-value"
                >
                  {hasScores ? stats.bestScore : "N/A"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Encouraging message for empty state */}
      {cvs.length === 0 && (
        <p
          className="text-center text-gray-500 mt-4"
          data-testid="stats-empty-message"
        >
          Upload your first CV to start tracking your progress!
        </p>
      )}
    </div>
  );
}

// Export for testing
export { calculateStats };
