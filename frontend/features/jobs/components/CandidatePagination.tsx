"use client";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface CandidatePaginationProps {
  total: number;
  limit: number;
  offset: number;
  onPageChange: (newOffset: number) => void;
  onPageSizeChange: (newLimit: number) => void;
}

export function CandidatePagination({
  total,
  limit,
  offset,
  onPageChange,
  onPageSizeChange,
}: CandidatePaginationProps) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);
  const startItem = total === 0 ? 0 : offset + 1;
  const endItem = Math.min(offset + limit, total);

  const canGoPrevious = offset > 0;
  const canGoNext = offset + limit < total;

  const handlePrevious = () => {
    if (canGoPrevious) {
      onPageChange(Math.max(0, offset - limit));
    }
  };

  const handleNext = () => {
    if (canGoNext) {
      onPageChange(offset + limit);
    }
  };

  const handlePageSizeChange = (value: string) => {
    const newLimit = parseInt(value, 10);
    onPageSizeChange(newLimit);
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
      {/* Info */}
      <div className="text-sm text-muted-foreground">
        {total > 0 ? (
          <span>
            Hiển thị {startItem}-{endItem} của {total} ứng viên
          </span>
        ) : (
          <span>Không có ứng viên</span>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        {/* Page Size */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Hiển thị:</span>
          <Select
            value={limit.toString()}
            onValueChange={handlePageSizeChange}
          >
            <SelectTrigger className="w-20" aria-label="Page size">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="50">50</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevious}
            disabled={!canGoPrevious}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground min-w-[80px] text-center">
            Trang {currentPage} / {totalPages || 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNext}
            disabled={!canGoNext}
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
