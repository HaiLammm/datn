/**
 * Interview History Page
 * 
 * Displays a paginated, filterable, and sortable list of completed interview sessions.
 * Implements Story 8.4: Interview History
 * 
 * Features:
 * - Grid layout (3 columns on desktop, 1 on mobile)
 * - Pagination controls
 * - Sorting (Most Recent, Highest Score)
 * - Status filtering (All, Completed, In Progress)
 * - Empty state handling
 * - Server-side rendering with auth protection
 */

import { redirect } from "next/navigation";
import Link from "next/link";
import { getSession } from "@/lib/auth";
import { getInterviewHistoryAction } from "@/features/interviews/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { InterviewSessionCard } from "@/features/interviews/components/InterviewSessionCard";
import { History, Plus, ChevronLeft, ChevronRight } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PageProps {
  searchParams: {
    page?: string;
    sort?: string;
    status?: string;
  };
}

export default async function InterviewHistoryPage({ searchParams }: PageProps) {
  // Auth check
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }

  // Parse search params
  const page = parseInt(searchParams.page || "1", 10);
  const sortOption = searchParams.sort || "recent";
  const statusFilter = searchParams.status || "all";

  // Map UI options to API params
  const sortBy: "created_at" | "overall_score" = sortOption === "score" ? "overall_score" : "created_at";
  const sortOrder: "asc" | "desc" = sortOption === "score" ? "desc" : "desc";
  const status = statusFilter !== "all" ? statusFilter : undefined;

  // Fetch interview history
  const result = await getInterviewHistoryAction({
    page,
    page_size: 12,
    sort_by: sortBy,
    sort_order: sortOrder,
    status,
  });

  const data = result.data;
  const error = result.error;
  const interviews = data?.items || [];
  const totalPages = data?.total_pages || 1;

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <History className="h-8 w-8" />
              Lịch sử phỏng vấn
            </h1>
            <p className="text-gray-600 mt-2">
              Xem lại các buổi phỏng vấn đã hoàn thành và phân tích chi tiết
            </p>
          </div>
          <Button asChild>
            <Link href="/interviews/new">
              <Plus className="h-4 w-4 mr-2" />
              Phỏng vấn mới
            </Link>
          </Button>
        </div>

        {/* Filters and Sorting */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          {/* Status Filter */}
          <div className="flex-1">
            <FilterSelect
              label="Trạng thái"
              value={statusFilter}
              options={[
                { value: "all", label: "Tất cả" },
                { value: "completed", label: "Hoàn thành" },
                { value: "in_progress", label: "Đang thực hiện" },
              ]}
              paramName="status"
              currentPage={page}
              currentSort={sortOption}
            />
          </div>

          {/* Sort Select */}
          <div className="flex-1">
            <FilterSelect
              label="Sắp xếp"
              value={sortOption}
              options={[
                { value: "recent", label: "Mới nhất" },
                { value: "score", label: "Điểm cao nhất" },
              ]}
              paramName="sort"
              currentPage={page}
              currentStatus={statusFilter}
            />
          </div>
        </div>

        {/* Error State */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="py-6">
              <p className="text-red-800">Lỗi: {error}</p>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!error && interviews.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <History className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Chưa có buổi phỏng vấn nào
              </h3>
              <p className="text-gray-600 mb-6">
                Bắt đầu buổi phỏng vấn đầu tiên để nhận phản hồi chi tiết từ AI
              </p>
              <Button asChild>
                <Link href="/interviews/new">
                  <Plus className="h-4 w-4 mr-2" />
                  Bắt đầu phỏng vấn
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Interviews Grid */}
        {!error && interviews.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {interviews.map((interview) => (
                <InterviewSessionCard key={interview.id} session={interview} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                {/* Previous Button */}
                <Button
                  asChild
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                >
                  <Link
                    href={`/interviews/history?page=${page - 1}&sort=${sortOption}&status=${statusFilter}`}
                    aria-disabled={page <= 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Link>
                </Button>

                {/* Page Numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNumber = i + 1;
                  const isActive = pageNumber === page;

                  return (
                    <Button
                      key={pageNumber}
                      asChild
                      variant={isActive ? "default" : "outline"}
                      size="sm"
                    >
                      <Link
                        href={`/interviews/history?page=${pageNumber}&sort=${sortOption}&status=${statusFilter}`}
                      >
                        {pageNumber}
                      </Link>
                    </Button>
                  );
                })}

                {/* Ellipsis if more pages */}
                {totalPages > 5 && (
                  <>
                    <span className="px-2 text-gray-500">...</span>
                    <Button asChild variant="outline" size="sm">
                      <Link
                        href={`/interviews/history?page=${totalPages}&sort=${sortOption}&status=${statusFilter}`}
                      >
                        {totalPages}
                      </Link>
                    </Button>
                  </>
                )}

                {/* Next Button */}
                <Button
                  asChild
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                >
                  <Link
                    href={`/interviews/history?page=${page + 1}&sort=${sortOption}&status=${statusFilter}`}
                    aria-disabled={page >= totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            )}

            {/* Results Summary */}
            <div className="text-center mt-4 text-sm text-gray-600">
              Trang {page} / {totalPages} • Tổng {data?.total || 0} buổi phỏng vấn
            </div>
          </>
        )}
      </div>
    </main>
  );
}

/**
 * Filter/Sort Select Component
 */
function FilterSelect({
  label,
  value,
  options,
  paramName,
  currentPage,
  currentSort,
  currentStatus,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  paramName: string;
  currentPage?: number;
  currentSort?: string;
  currentStatus?: string;
}) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700 mb-2 block">{label}</label>
      <Select value={value}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => {
            // Build URL with updated param
            const params = new URLSearchParams();
            if (paramName === "sort") {
              params.set("sort", option.value);
              if (currentStatus && currentStatus !== "all") params.set("status", currentStatus);
            } else if (paramName === "status") {
              params.set("status", option.value);
              if (currentSort && currentSort !== "recent") params.set("sort", currentSort);
            }
            params.set("page", "1"); // Reset to page 1 on filter change

            return (
              <SelectItem key={option.value} value={option.value}>
                <Link href={`/interviews/history?${params.toString()}`} className="block w-full">
                  {option.label}
                </Link>
              </SelectItem>
            );
          })}
        </SelectContent>
      </Select>
    </div>
  );
}
