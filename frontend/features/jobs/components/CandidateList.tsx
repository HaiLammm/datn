"use client";

import { useState, useEffect, useCallback } from "react";
import {
  RankedCandidateResponse,
  RankedCandidateListResponse,
} from "@datn/shared-types";
import { getCandidatesAction } from "@/features/jobs/actions";
import { CandidateCard } from "./CandidateCard";
import { CandidatePagination } from "./CandidatePagination";
import { MinScoreFilter } from "./MinScoreFilter";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, AlertCircle, Users } from "lucide-react";

interface CandidateListProps {
  jdId: string;
  initialData?: RankedCandidateListResponse;
}

export function CandidateList({ jdId, initialData }: CandidateListProps) {
  const [candidates, setCandidates] = useState<RankedCandidateResponse[]>(
    initialData?.items || []
  );
  const [total, setTotal] = useState(initialData?.total || 0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(initialData?.offset || 0);
  const [limit, setLimit] = useState(initialData?.limit || 20);
  const [minScore, setMinScore] = useState(0);

  const fetchCandidates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getCandidatesAction(jdId, {
        limit,
        offset,
        min_score: minScore > 0 ? minScore : undefined,
      });
      if (result) {
        setCandidates(result.items);
        setTotal(result.total);
      } else {
        setError("Không thể tải danh sách ứng viên. Vui lòng thử lại.");
      }
    } catch (err) {
      console.error("Error fetching candidates:", err);
      setError("Đã xảy ra lỗi khi tải danh sách ứng viên.");
    } finally {
      setLoading(false);
    }
  }, [jdId, limit, offset, minScore]);

  // Fetch when params change (except initial load)
  useEffect(() => {
    // Skip initial fetch if we have initial data
    if (initialData && offset === 0 && limit === 20 && minScore === 0) {
      return;
    }
    fetchCandidates();
  }, [fetchCandidates, initialData, offset, limit, minScore]);

  const handlePageChange = (newOffset: number) => {
    setOffset(newOffset);
  };

  const handlePageSizeChange = (newLimit: number) => {
    setLimit(newLimit);
    setOffset(0); // Reset to first page
  };

  const handleMinScoreChange = (newMinScore: number) => {
    setMinScore(newMinScore);
    setOffset(0); // Reset to first page
  };

  const handleRetry = () => {
    fetchCandidates();
  };

  // Loading State
  if (loading && candidates.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <span className="ml-2 text-muted-foreground">
            Đang tải danh sách ứng viên...
          </span>
        </div>
      </div>
    );
  }

  // Error State
  if (error && candidates.length === 0) {
    return (
      <Card className="p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Đã xảy ra lỗi
        </h3>
        <p className="text-muted-foreground mb-4">{error}</p>
        <Button onClick={handleRetry} variant="outline">
          Thử lại
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="p-4">
        <MinScoreFilter value={minScore} onChange={handleMinScoreChange} />
      </Card>

      {/* Loading overlay for subsequent fetches */}
      {loading && candidates.length > 0 && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Đang cập nhật...</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && candidates.length === 0 && (
        <Card className="p-8 text-center">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Không tìm thấy ứng viên phù hợp
          </h3>
          <p className="text-muted-foreground">
            {minScore > 0
              ? `Không có ứng viên nào đạt điểm tối thiểu ${minScore}%. Hãy thử giảm điểm tối thiểu.`
              : "Chưa có CV nào trong hệ thống hoặc chưa có ứng viên phù hợp với JD này."}
          </p>
        </Card>
      )}

      {/* Candidates List */}
      {candidates.length > 0 && (
        <>
          <div className="space-y-4">
            {candidates.map((candidate, index) => (
              <CandidateCard
                key={candidate.cv_id}
                candidate={candidate}
                rank={offset + index + 1}
                jdId={jdId}
              />
            ))}
          </div>

          {/* Pagination */}
          <CandidatePagination
            total={total}
            limit={limit}
            offset={offset}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
          />
        </>
      )}
    </div>
  );
}
