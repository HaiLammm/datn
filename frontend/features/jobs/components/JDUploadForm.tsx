"use client";

import { useActionState, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { createJDAction, ActionState } from "@/features/jobs/actions";
import { Loader2, Upload, FileText, X } from "lucide-react";

type InputMode = "text" | "file";

const initialState: ActionState = {
  message: "",
  errors: {},
};

export function JDUploadForm() {
  const router = useRouter();
  const [state, formAction, isPending] = useActionState(
    createJDAction,
    initialState
  );
  const [inputMode, setInputMode] = useState<InputMode>("text");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string>("");
  const [locationType, setLocationType] = useState<string>("remote");

  // Handle successful submission - redirect to JD detail page
  useEffect(() => {
    if (state.data?.id) {
      router.push(`/jobs/jd/${state.data.id}`);
    }
  }, [state.data, router]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      // Validate file type
      if (
        file.type === "application/pdf" ||
        file.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      ) {
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          setSelectedFile(null);
          setFileError("Kích thước file tối đa là 10MB.");
        } else {
          setSelectedFile(file);
          setFileError("");
        }
      } else {
        setSelectedFile(null);
        setFileError("Chỉ chấp nhận file PDF hoặc DOCX.");
      }
    } else {
      setSelectedFile(null);
      setFileError("");
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setFileError("");
    // Reset file input
    const fileInput = document.getElementById("jdFile") as HTMLInputElement;
    if (fileInput) {
      fileInput.value = "";
    }
  };

  const isSubmitDisabled =
    isPending ||
    (inputMode === "file" && !selectedFile);

  return (
    <form
      action={formAction}
      className="space-y-6 p-6 border rounded-lg shadow-sm bg-white"
    >
      <h2 className="text-2xl font-semibold text-gray-900">
        Tạo Job Description mới
      </h2>

      {/* Hidden input for input mode */}
      <input type="hidden" name="inputMode" value={inputMode} />

      {/* Title Field */}
      <div className="space-y-2">
        <Label htmlFor="title">
          Tiêu đề <span className="text-red-500">*</span>
        </Label>
        <Input
          id="title"
          name="title"
          type="text"
          placeholder="VD: Senior Python Developer"
          aria-describedby="title-error"
          className="w-full"
        />
        {state?.errors?.title && (
          <p id="title-error" role="alert" className="text-red-500 text-sm">
            {state.errors.title}
          </p>
        )}
      </div>

      {/* Input Mode Toggle */}
      <div className="space-y-3">
        <Label>Nhập mô tả công việc:</Label>
        <RadioGroup
          value={inputMode}
          onValueChange={(value) => setInputMode(value as InputMode)}
          className="flex flex-wrap gap-4"
          aria-label="Chọn phương thức nhập mô tả"
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="text" id="text-mode" />
            <Label htmlFor="text-mode" className="cursor-pointer flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Paste văn bản
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="file" id="file-mode" />
            <Label htmlFor="file-mode" className="cursor-pointer flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Tải file lên (PDF/DOCX)
            </Label>
          </div>
        </RadioGroup>
      </div>

      {/* Conditional: Text Input or File Upload */}
      {inputMode === "text" ? (
        <div className="space-y-2">
          <Label htmlFor="description">
            Mô tả công việc <span className="text-red-500">*</span>
          </Label>
          <Textarea
            id="description"
            name="description"
            placeholder="Paste nội dung JD vào đây..."
            rows={8}
            aria-describedby="description-error"
            className="w-full resize-y"
          />
          {state?.errors?.description && (
            <p
              id="description-error"
              role="alert"
              className="text-red-500 text-sm"
            >
              {state.errors.description}
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <Label htmlFor="jdFile">
            Chọn file JD <span className="text-red-500">*</span>
          </Label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
            {selectedFile ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="h-8 w-8 text-blue-500" />
                <span className="text-gray-700">{selectedFile.name}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={clearFile}
                  aria-label="Xóa file đã chọn"
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <>
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 mb-2">
                  Kéo thả file vào đây hoặc click để chọn
                </p>
                <p className="text-gray-400 text-sm">
                  Hỗ trợ PDF, DOCX (tối đa 10MB)
                </p>
              </>
            )}
            <Input
              id="jdFile"
              name="jdFile"
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileChange}
              className={selectedFile ? "hidden" : "mt-3 cursor-pointer"}
              aria-describedby="file-error"
            />
          </div>
          {fileError && (
            <p id="file-error" role="alert" className="text-red-500 text-sm">
              {fileError}
            </p>
          )}
          {state?.errors?.jdFile && (
            <p role="alert" className="text-red-500 text-sm">
              {state.errors.jdFile}
            </p>
          )}
        </div>
      )}

      {/* Two-column layout for optional fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Location Type */}
        <div className="space-y-2">
          <Label htmlFor="location_type">Hình thức làm việc</Label>
          <Select
            name="location_type"
            value={locationType}
            onValueChange={setLocationType}
          >
            <SelectTrigger id="location_type" aria-label="Chọn hình thức làm việc">
              <SelectValue placeholder="Chọn hình thức" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="remote">Remote</SelectItem>
              <SelectItem value="hybrid">Hybrid</SelectItem>
              <SelectItem value="on-site">On-site</SelectItem>
            </SelectContent>
          </Select>
          {state?.errors?.location_type && (
            <p role="alert" className="text-red-500 text-sm">
              {state.errors.location_type}
            </p>
          )}
        </div>

        {/* Min Experience Years */}
        <div className="space-y-2">
          <Label htmlFor="min_experience_years">
            Kinh nghiệm tối thiểu (năm)
          </Label>
          <Input
            id="min_experience_years"
            name="min_experience_years"
            type="number"
            min="0"
            placeholder="VD: 3"
            aria-describedby="min-exp-help"
          />
          <p id="min-exp-help" className="text-gray-400 text-xs">
            Không bắt buộc
          </p>
        </div>
      </div>

      {/* Required Skills */}
      <div className="space-y-2">
        <Label htmlFor="required_skills">Kỹ năng yêu cầu</Label>
        <Input
          id="required_skills"
          name="required_skills"
          type="text"
          placeholder="VD: Python, FastAPI, PostgreSQL (phân cách bằng dấu phẩy)"
          aria-describedby="skills-help"
        />
        <p id="skills-help" className="text-gray-400 text-xs">
          Không bắt buộc - Các kỹ năng phân cách bằng dấu phẩy
        </p>
      </div>

      {/* Salary Range */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="salary_min">Mức lương tối thiểu (USD)</Label>
          <Input
            id="salary_min"
            name="salary_min"
            type="number"
            min="0"
            placeholder="VD: 2000"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="salary_max">Mức lương tối đa (USD)</Label>
          <Input
            id="salary_max"
            name="salary_max"
            type="number"
            min="0"
            placeholder="VD: 4000"
          />
        </div>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={isSubmitDisabled}
        className="w-full"
        aria-busy={isPending}
      >
        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isPending ? "Đang tạo..." : "Tạo Job Description"}
      </Button>

      {/* Status Message */}
      {state?.message && !state.data && (
        <p
          role="alert"
          aria-live="polite"
          className={`text-sm mt-2 ${
            state.message.includes("thành công")
              ? "text-green-600"
              : "text-red-500"
          }`}
        >
          {state.message}
        </p>
      )}
    </form>
  );
}
