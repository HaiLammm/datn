"use client";

import Link from "next/link";
import { useState } from "react";
import { JobDescriptionResponse, JDParseStatus } from "@datn/shared-types";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { deleteJDAction } from "@/features/jobs/actions";
import {
  Trash2,
  MapPin,
  Clock,
  Briefcase,
  Loader2,
} from "lucide-react";

interface JDCardProps {
  jd: JobDescriptionResponse;
  onDelete?: () => void;
}

const statusConfig: Record<
  JDParseStatus,
  { label: string; color: string; bgColor: string }
> = {
  pending: {
    label: "Chờ xử lý",
    color: "text-yellow-700",
    bgColor: "bg-yellow-100",
  },
  processing: {
    label: "Đang phân tích",
    color: "text-blue-700",
    bgColor: "bg-blue-100",
  },
  completed: {
    label: "Hoàn thành",
    color: "text-green-700",
    bgColor: "bg-green-100",
  },
  failed: {
    label: "Thất bại",
    color: "text-red-700",
    bgColor: "bg-red-100",
  },
};

const locationTypeLabels: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  "on-site": "On-site",
};

export function JDCard({ jd, onDelete }: JDCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const status = statusConfig[jd.parse_status] || statusConfig.pending;
  const skillCount = jd.parsed_requirements?.required_skills?.length || 0;
  const uploadedDate = new Date(jd.uploaded_at).toLocaleDateString("vi-VN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const handleDelete = async () => {
    setIsDeleting(true);
    setDeleteError(null);
    try {
      const result = await deleteJDAction(jd.id);
      if (result.success) {
        onDelete?.();
      } else {
        setDeleteError(result.message);
      }
    } catch (error) {
      setDeleteError("Đã xảy ra lỗi khi xóa JD.");
      console.error("Delete error:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card className="p-5 hover:shadow-md transition-shadow">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <Link
              href={`/jobs/jd/${jd.id}`}
              className="block group"
            >
              <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                {jd.title}
              </h3>
            </Link>
          </div>
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}
            aria-label={`Trạng thái: ${status.label}`}
          >
            {status.label}
          </span>
        </div>

        {/* Meta info */}
        <div className="flex flex-wrap gap-3 text-sm text-gray-500 mb-4">
          <span className="flex items-center gap-1">
            <MapPin className="h-4 w-4" aria-hidden="true" />
            {locationTypeLabels[jd.location_type] || jd.location_type}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" aria-hidden="true" />
            {uploadedDate}
          </span>
          {skillCount > 0 && (
            <span className="flex items-center gap-1">
              <Briefcase className="h-4 w-4" aria-hidden="true" />
              {skillCount} kỹ năng
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 mt-auto pt-3 border-t">
          <Link href={`/jobs/jd/${jd.id}`} className="flex-1">
            <Button variant="outline" className="w-full" size="sm">
              Xem chi tiết
            </Button>
          </Link>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="text-red-500 hover:text-red-700 hover:bg-red-50"
                aria-label={`Xóa JD: ${jd.title}`}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Xác nhận xóa</AlertDialogTitle>
                <AlertDialogDescription>
                  Bạn có chắc chắn muốn xóa JD &quot;{jd.title}&quot;? Hành động
                  này không thể hoàn tác.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Hủy</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDelete}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Xóa
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>

        {/* Delete error */}
        {deleteError && (
          <p role="alert" className="text-red-500 text-sm mt-2">
            {deleteError}
          </p>
        )}
      </div>
    </Card>
  );
}
