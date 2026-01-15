"use client";

import { useActionState, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createCVAction } from "@/features/cv/actions";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export function CVUploadForm() {
  const [state, formAction, isPending] = useActionState(createCVAction, {
    message: "",
    errors: {},
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string>("");

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

  return (
    <form action={formAction} className="space-y-4 p-4 border rounded-md shadow-sm">
      <h2 className="text-xl font-semibold">Tải lên CV của bạn</h2>

      <div>
        <Label htmlFor="cvFile">Chọn file CV (PDF hoặc DOCX)</Label>
        <Input
          id="cvFile"
          name="cvFile"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
          disabled={isPending}
          className="mt-1"
        />
        {fileError && (
          <p className="text-red-500 text-sm mt-1">{fileError}</p>
        )}
        {state?.errors?.cvFile && (
          <p className="text-red-500 text-sm mt-1">{state.errors.cvFile}</p>
        )}
        {selectedFile && !fileError && (
          <p className="text-gray-600 text-sm mt-1">
            Đã chọn: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      <Button
        type="submit"
        disabled={isPending || !selectedFile || !!fileError}
        className="w-full"
      >
        {isPending && <LoadingSpinner size="sm" className="mr-2" />}
        {isPending ? "Đang tải lên..." : "Tải lên CV"}
      </Button>

      {state?.message && (
        <p
          className={`text-sm mt-2 ${
            state.message.includes("thành công") ? "text-green-600" : "text-red-500"
          }`}
        >
          {state.message}
        </p>
      )}
    </form>
  );
}
