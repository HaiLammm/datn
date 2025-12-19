"use client";

import Link from "next/link";
import { CVWithStatus } from "@datn/shared-types";
import { FileText, Upload, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getScoreColor, getScoreDisplay, formatDate } from "./CVHistoryCard";

interface RecentCVsPreviewProps {
  cvs: CVWithStatus[];
  limit?: number;
}

export function RecentCVsPreview({ cvs, limit = 3 }: RecentCVsPreviewProps) {
  const recentCvs = cvs.slice(0, limit);

  if (cvs.length === 0) {
    return (
      <Card data-testid="recent-cvs-empty">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Recent CVs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 mb-4" data-testid="empty-state-message">
              No CVs yet. Upload your first CV to get started!
            </p>
            <Button asChild>
              <Link href="/cvs/upload">
                <Upload className="h-4 w-4 mr-2" />
                Upload CV
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card data-testid="recent-cvs-preview">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
                    Gần đây
        </CardTitle>
        <Link
          href="/cvs"
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          data-testid="view-all-link"
        >
          View All
          <ArrowRight className="h-4 w-4" />
        </Link>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {recentCvs.map((cv) => (
            <Link
              key={cv.id}
              href={`/cvs/${cv.id}/analysis`}
              className="block p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-gray-50 transition-colors"
              data-testid="cv-preview-item"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate" data-testid="cv-filename">
                    {cv.filename}
                  </p>
                  <p className="text-sm text-gray-500" data-testid="cv-date">
                    {formatDate(cv.uploaded_at)}
                  </p>
                </div>
                <div className="ml-4 text-right">
                  <span
                    className={`text-lg font-semibold ${getScoreColor(cv.quality_score)}`}
                    data-testid="cv-score"
                  >
                    {getScoreDisplay(cv.quality_score, cv.analysis_status)}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
