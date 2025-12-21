"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { useFileUpload } from "@/lib/hooks/useFileUpload";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export function CVUploadForm() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string>("");
  const { isUploading, progress, error, isSuccess, upload, reset } = useFileUpload();

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return "Chỉ chấp nhận file PDF hoặc DOCX.";
    }
    if (file.size > MAX_FILE_SIZE) {
      return "Kích thước file tối đa là 5MB.";
    }
    return null;
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    reset(); // Clear any previous upload state

    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      const validationError = validateFile(file);

      if (validationError) {
        setSelectedFile(null);
        setFileError(validationError);
      } else {
        setSelectedFile(file);
        setFileError("");
      }
    } else {
      setSelectedFile(null);
      setFileError("");
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!selectedFile) {
      setFileError("Vui lòng chọn file CV.");
      return;
    }

    const validationError = validateFile(selectedFile);
    if (validationError) {
      setFileError(validationError);
      return;
    }

    await upload({
      file: selectedFile,
      url: "/api/cvs/upload",
      fieldName: "file",
      onSuccess: () => {
        toast.success("CV đã được tải lên thành công!");
        // Reset form
        setSelectedFile(null);
        const fileInput = document.getElementById("cvFile") as HTMLInputElement;
        if (fileInput) fileInput.value = "";
        // Redirect to CV list
        router.push("/cvs");
        router.refresh();
      },
      onError: (errorMessage) => {
        toast.error(errorMessage);
      },
    });
  };

  const handleRetry = () => {
    reset();
    if (selectedFile) {
      handleSubmit(new Event("submit") as unknown as React.FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-md shadow-sm">
      <h2 className="text-xl font-semibold">Tải lên CV của bạn</h2>

      <div>
        <Label htmlFor="cvFile">Chọn file CV (PDF hoặc DOCX)</Label>
        <Input
          id="cvFile"
          name="cvFile"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
          disabled={isUploading}
          className="mt-1"
        />
        {fileError && (
          <p className="text-red-500 text-sm mt-1">{fileError}</p>
        )}
        {selectedFile && !fileError && (
          <p className="text-gray-600 text-sm mt-1">
            Đã chọn: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-2" data-testid="upload-progress">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Đang tải lên...</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} size="md" />
        </div>
      )}

      {/* Success State */}
      {isSuccess && (
        <div className="p-3 bg-green-50 text-green-700 rounded-md text-sm" data-testid="upload-success">
          CV đã được tải lên thành công! Đang chuyển hướng...
        </div>
      )}

      {/* Error State with Retry */}
      {error && !isUploading && (
        <ErrorDisplay
          message={error}
          onRetry={handleRetry}
          retryText="Thử lại"
          data-testid="upload-error"
        />
      )}

      <Button
        type="submit"
        disabled={isUploading || !selectedFile || !!fileError}
        className="w-full"
      >
        {isUploading && <LoadingSpinner size="sm" className="mr-2" />}
        {isUploading ? "Đang tải lên..." : "Tải lên CV"}
      </Button>
    </form>
  );
}
