"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { QuickActions } from "./QuickActions";

interface DashboardErrorProps {
  error: Error;
  retry: () => void;
}

export function DashboardError({ error, retry }: DashboardErrorProps) {
  return (
    <div className="space-y-8" data-testid="dashboard-error">
      {/* Quick Actions still work even when data fails to load */}
      <QuickActions />

      {/* Error Message */}
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="text-center py-4">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-700 mb-2">
              Failed to load dashboard data
            </h3>
            <p className="text-red-600 mb-4" data-testid="error-message">
              {error.message || "An unexpected error occurred. Please try again."}
            </p>
            <Button
              onClick={retry}
              variant="outline"
              className="border-red-300 text-red-700 hover:bg-red-100"
              data-testid="retry-button"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
