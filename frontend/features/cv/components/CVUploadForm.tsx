"use client";

import { useActionState, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createCVAction } from "@/features/cv/actions"; // Assuming this action exists
import { Loader2 } from "lucide-react"; // Assuming lucide-react is installed

export function CVUploadForm() {
    const [state, formAction, isPending] = useActionState(createCVAction, {
        message: "",
        errors: {},
    });
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileError, setFileError] = useState<string>("");

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            const file = event.target.files[0];
            // Basic client-side validation for file type
            if (
                file.type === "application/pdf" ||
                file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ) {
                setSelectedFile(file);
                setFileError("");
            } else {
                setSelectedFile(null);
                setFileError("Chỉ chấp nhận file PDF hoặc DOCX.");
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
                    className="mt-1"
                />
                {fileError && (
                    <p className="text-red-500 text-sm mt-1">{fileError}</p>
                )}
                {state?.errors?.cvFile && (
                    <p className="text-red-500 text-sm mt-1">{state.errors.cvFile}</p>
                )}
            </div>

            <Button type="submit" disabled={isPending || !selectedFile} className="w-full">
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
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
