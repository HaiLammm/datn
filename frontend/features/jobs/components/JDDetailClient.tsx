"use client";

import { useState } from "react";
import { toast } from "sonner";
import { JobDescriptionResponse, ParsedJDRequirements } from "@datn/shared-types";
import { ParseStatusDisplay } from "@/features/jobs/components/ParseStatusDisplay";
import { EditParsedRequirements } from "@/features/jobs/components/EditParsedRequirements";
import { deleteJDAction } from "@/features/jobs/actions";
import { Button } from "@/components/ui/button";
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
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  MapPin,
  DollarSign,
  Calendar,
  Trash2,
  Users,
  Loader2,
} from "lucide-react";

interface JDDetailClientProps {
  jd: JobDescriptionResponse;
}

const locationTypeLabels: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  "on-site": "On-site",
};

export function JDDetailClient({ jd }: JDDetailClientProps) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [currentRequirements] = useState<ParsedJDRequirements | null>(
    jd.parsed_requirements as ParsedJDRequirements | null
  );

  const uploadedDate = new Date(jd.uploaded_at).toLocaleDateString("vi-VN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      const result = await deleteJDAction(jd.id);
      if (result.success) {
        toast.success(`JD "${jd.title}" has been deleted`);
        router.push("/jobs");
      } else {
        toast.error(result.message || "Failed to delete JD");
      }
    } catch (error) {
      toast.error("An unexpected error occurred");
      console.error("Delete error:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEditSave = () => {
    setIsEditing(false);
    // Refresh page to get updated data
    router.refresh();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <Link
            href="/jobs"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lại danh sách
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{jd.title}</h1>
        </div>

        <div className="flex gap-2">
          {jd.parse_status === "completed" ? (
            <Link href={`/jobs/jd/${jd.id}/candidates`}>
              <Button variant="default">
                <Users className="h-4 w-4 mr-2" />
                Xem ứng viên phù hợp
              </Button>
            </Link>
          ) : (
            <Button
              variant="default"
              disabled
              title="JD cần được phân tích hoàn tất trước khi xem ứng viên"
            >
              <Users className="h-4 w-4 mr-2" />
              Xem ứng viên phù hợp
            </Button>
          )}

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="outline"
                className="text-red-500 hover:text-red-700 hover:border-red-300"
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
                  Bạn có chắc chắn muốn xóa JD &quot;{jd.title}&quot;? Hành động này
                  không thể hoàn tác.
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
      </div>

      {/* Meta Info */}
      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
        <span className="flex items-center gap-1">
          <MapPin className="h-4 w-4" aria-hidden="true" />
          {locationTypeLabels[jd.location_type] || jd.location_type}
        </span>
        <span className="flex items-center gap-1">
          <Calendar className="h-4 w-4" aria-hidden="true" />
          {uploadedDate}
        </span>
        {(jd.salary_min || jd.salary_max) && (
          <span className="flex items-center gap-1">
            <DollarSign className="h-4 w-4" aria-hidden="true" />
            {jd.salary_min && jd.salary_max
              ? `$${jd.salary_min} - $${jd.salary_max}`
              : jd.salary_min
              ? `Từ $${jd.salary_min}`
              : `Đến $${jd.salary_max}`}
          </span>
        )}
      </div>

      {/* Description */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Mô tả công việc
        </h2>
        <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
          {jd.description}
        </div>
      </div>

      {/* Parse Status / Edit Mode */}
      {isEditing && currentRequirements ? (
        <EditParsedRequirements
          jdId={jd.id}
          currentRequirements={currentRequirements}
          onSave={handleEditSave}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <ParseStatusDisplay
          jdId={jd.id}
          initialStatus={jd.parse_status}
          initialParsedRequirements={currentRequirements}
          onEditClick={() => setIsEditing(true)}
        />
      )}
    </div>
  );
}
