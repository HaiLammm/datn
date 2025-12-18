"use client";

import { SearchResultResponse } from "@datn/shared-types";
import { SearchResultCard } from "./SearchResultCard";
import { CandidatePagination } from "./CandidatePagination";
import { MinScoreFilter } from "./MinScoreFilter";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RefreshCw, SearchX } from "lucide-react";

export interface SearchResultListProps {
  results: SearchResultResponse[];
  total: number;
  loading: boolean;
  error: string | null;
  limit: number;
  offset: number;
  minScore: number;
  onPageChange: (newOffset: number) => void;
  onPageSizeChange: (newLimit: number) => void;
  onMinScoreChange: (newMinScore: number) => void;
  onRetry?: () => void;
}

function SkeletonCard() {
  return (
    <Card data-testid="skeleton-card">
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex sm:flex-col items-center gap-3">
            <Skeleton className="h-6 w-8" />
            <Skeleton className="h-10 w-10 rounded-full" />
          </div>
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex gap-1 pt-1">
              <Skeleton className="h-5 w-16" />
              <Skeleton className="h-5 w-16" />
              <Skeleton className="h-5 w-16" />
            </div>
          </div>
          <div className="flex sm:flex-col justify-end">
            <Skeleton className="h-8 w-20" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyState() {
  return (
    <Card className="border-dashed">
      <CardContent className="py-12 flex flex-col items-center justify-center text-center">
        <SearchX
          className="h-12 w-12 text-muted-foreground mb-4"
          aria-hidden="true"
        />
        <h3 className="text-lg font-medium mb-2">
          Khong tim thay ung vien phu hop
        </h3>
        <p className="text-sm text-muted-foreground max-w-md mb-4">
          Thu:
        </p>
        <ul className="text-sm text-muted-foreground text-left space-y-1">
          <li>- Su dung cac tu khoa khac</li>
          <li>- Giam diem toi thieu</li>
          <li>- Mo rong pham vi ky nang</li>
        </ul>
      </CardContent>
    </Card>
  );
}

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
}

function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <Card className="border-destructive/50 bg-destructive/5">
      <CardContent className="py-8 flex flex-col items-center justify-center text-center">
        <AlertCircle
          className="h-12 w-12 text-destructive mb-4"
          aria-hidden="true"
        />
        <h3 className="text-lg font-medium text-destructive mb-2">
          Co loi xay ra
        </h3>
        <p className="text-sm text-muted-foreground mb-4">{error}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Thu lai
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

export function SearchResultList({
  results,
  total,
  loading,
  error,
  limit,
  offset,
  minScore,
  onPageChange,
  onPageSizeChange,
  onMinScoreChange,
  onRetry,
}: SearchResultListProps) {
  // Show loading skeleton
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-64" />
        </div>
        <div role="list" aria-label="Dang tai ket qua" className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  // Show empty state
  if (results.length === 0 && total === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      {/* Header with total count and filter */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <p className="text-sm font-medium">
          Tim thay <span className="text-primary">{total}</span> ung vien phu
          hop
        </p>
        <MinScoreFilter value={minScore} onChange={onMinScoreChange} />
      </div>

      {/* Results list */}
      <div role="list" aria-label="Danh sach ket qua tim kiem" className="space-y-3">
        {results.map((result, index) => (
          <SearchResultCard
            key={result.cv_id}
            result={result}
            rank={offset + index + 1}
          />
        ))}
      </div>

      {/* Pagination */}
      {total > 0 && (
        <CandidatePagination
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={onPageChange}
          onPageSizeChange={onPageSizeChange}
        />
      )}
    </div>
  );
}
