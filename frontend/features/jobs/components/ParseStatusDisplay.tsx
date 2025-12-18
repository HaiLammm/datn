"use client";

import { useState, useEffect, useCallback } from "react";
import {
  JDParseStatus,
  ParsedJDRequirements,
  JDParseStatusResponse,
} from "@datn/shared-types";
import { getJDParseStatusAction } from "@/features/jobs/actions";
import { Button } from "@/components/ui/button";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Edit3,
  Briefcase,
  Star,
  Calendar,
  ListChecks,
} from "lucide-react";

interface ParseStatusDisplayProps {
  jdId: string;
  initialStatus: JDParseStatus;
  initialParsedRequirements?: ParsedJDRequirements | null;
  onEditClick?: () => void;
}

const POLL_INTERVAL = 3000; // 3 seconds

export function ParseStatusDisplay({
  jdId,
  initialStatus,
  initialParsedRequirements,
  onEditClick,
}: ParseStatusDisplayProps) {
  const [status, setStatus] = useState<JDParseStatus>(initialStatus);
  const [parsedRequirements, setParsedRequirements] =
    useState<ParsedJDRequirements | null>(initialParsedRequirements || null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(
    initialStatus === "pending" || initialStatus === "processing"
  );

  const fetchStatus = useCallback(async () => {
    try {
      const result: JDParseStatusResponse | null =
        await getJDParseStatusAction(jdId);
      if (result) {
        setStatus(result.parse_status);
        if (result.parse_status === "completed" && result.parsed_requirements) {
          setParsedRequirements(result.parsed_requirements);
          setIsPolling(false);
        } else if (result.parse_status === "failed") {
          setParseError(result.parse_error || "Đã xảy ra lỗi khi phân tích JD.");
          setIsPolling(false);
        }
      }
    } catch (error) {
      console.error("Error fetching parse status:", error);
    }
  }, [jdId]);

  useEffect(() => {
    if (!isPolling) return;

    const interval = setInterval(fetchStatus, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [isPolling, fetchStatus]);

  // Render based on status
  if (status === "pending" || status === "processing") {
    return (
      <div
        className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center"
        aria-live="polite"
      >
        <Loader2
          className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-spin"
          aria-hidden="true"
        />
        <h3 className="text-lg font-medium text-blue-800 mb-2">
          {status === "pending" ? "Chờ xử lý..." : "Đang phân tích JD..."}
        </h3>
        <p className="text-blue-600 text-sm">
          Hệ thống đang phân tích JD của bạn. Vui lòng đợi...
        </p>
        <p className="text-blue-400 text-xs mt-2">
          (Thường mất 10-30 giây)
        </p>
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div
        className="bg-red-50 border border-red-200 rounded-lg p-6"
        role="alert"
      >
        <div className="flex items-start gap-3">
          <XCircle
            className="h-6 w-6 text-red-500 flex-shrink-0 mt-0.5"
            aria-hidden="true"
          />
          <div>
            <h3 className="text-lg font-medium text-red-800 mb-1">
              Phân tích thất bại
            </h3>
            <p className="text-red-600 text-sm">
              {parseError || "Đã xảy ra lỗi khi phân tích JD."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Status: completed
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CheckCircle2
            className="h-5 w-5 text-green-600"
            aria-hidden="true"
          />
          <h3 className="text-lg font-medium text-green-800">
            Phân tích hoàn tất
          </h3>
        </div>
        {onEditClick && (
          <Button
            variant="outline"
            size="sm"
            onClick={onEditClick}
            aria-label="Chỉnh sửa yêu cầu đã phân tích"
          >
            <Edit3 className="h-4 w-4 mr-1" />
            Chỉnh sửa
          </Button>
        )}
      </div>

      {parsedRequirements && (
        <div className="space-y-4">
          {/* Required Skills */}
          {parsedRequirements.required_skills &&
            parsedRequirements.required_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Briefcase
                    className="h-4 w-4 text-gray-500"
                    aria-hidden="true"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Kỹ năng yêu cầu:
                  </span>
                </div>
                <div
                  className="flex flex-wrap gap-2"
                  role="list"
                  aria-label="Danh sách kỹ năng yêu cầu"
                >
                  {parsedRequirements.required_skills.map((skill, index) => (
                    <span
                      key={index}
                      role="listitem"
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Nice-to-have Skills */}
          {parsedRequirements.nice_to_have_skills &&
            parsedRequirements.nice_to_have_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Star
                    className="h-4 w-4 text-gray-500"
                    aria-hidden="true"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Kỹ năng ưu tiên:
                  </span>
                </div>
                <div
                  className="flex flex-wrap gap-2"
                  role="list"
                  aria-label="Danh sách kỹ năng ưu tiên"
                >
                  {parsedRequirements.nice_to_have_skills.map((skill, index) => (
                    <span
                      key={index}
                      role="listitem"
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Min Experience */}
          {parsedRequirements.min_experience_years !== null && (
            <div className="flex items-center gap-2">
              <Calendar
                className="h-4 w-4 text-gray-500"
                aria-hidden="true"
              />
              <span className="text-sm text-gray-700">
                <span className="font-medium">Kinh nghiệm tối thiểu:</span>{" "}
                {parsedRequirements.min_experience_years} năm
              </span>
            </div>
          )}

          {/* Job Title Normalized */}
          {parsedRequirements.job_title_normalized && (
            <div className="flex items-center gap-2">
              <Clock
                className="h-4 w-4 text-gray-500"
                aria-hidden="true"
              />
              <span className="text-sm text-gray-700">
                <span className="font-medium">Tiêu đề chuẩn hóa:</span>{" "}
                {parsedRequirements.job_title_normalized}
              </span>
            </div>
          )}

          {/* Key Responsibilities */}
          {parsedRequirements.key_responsibilities &&
            parsedRequirements.key_responsibilities.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <ListChecks
                    className="h-4 w-4 text-gray-500"
                    aria-hidden="true"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Trách nhiệm chính:
                  </span>
                </div>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                  {parsedRequirements.key_responsibilities.map((resp, index) => (
                    <li key={index}>{resp}</li>
                  ))}
                </ul>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
