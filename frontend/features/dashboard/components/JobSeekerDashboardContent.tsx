"use client";

import { useState, useCallback } from "react";
import { CVWithStatus } from "@datn/shared-types";
import { QuickActions } from "./QuickActions";
import { DashboardStats } from "./DashboardStats";
import { DashboardError } from "./DashboardError";
import { RecentCVsPreview } from "@/features/cv/components/RecentCVsPreview";

interface JobSeekerDashboardContentProps {
  initialCvs: CVWithStatus[];
  initialError?: string;
  userEmail: string;
}

export function JobSeekerDashboardContent({
  initialCvs,
  initialError,
  userEmail,
}: JobSeekerDashboardContentProps) {
  const [cvs] = useState<CVWithStatus[]>(initialCvs);
  const [error, setError] = useState<Error | null>(
    initialError ? new Error(initialError) : null
  );

  const handleRetry = useCallback(async () => {
    try {
      setError(null);
      // Refresh the page to re-fetch data from server
      window.location.reload();
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Failed to refresh"));
    }
  }, []);

  if (error) {
    return <DashboardError error={error} retry={handleRetry} />;
  }

  return (
    <div className="space-y-8" data-testid="job-seeker-dashboard">
      {/* Welcome Message */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900" data-testid="welcome-message">
          Welcome back, {userEmail}!
        </h2>
        <p className="text-gray-600 mt-1">
          Here&apos;s an overview of your CV portfolio.
        </p>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Stats */}
      <DashboardStats cvs={cvs} />

      {/* Recent CVs */}
      <RecentCVsPreview cvs={cvs} limit={3} />
    </div>
  );
}
