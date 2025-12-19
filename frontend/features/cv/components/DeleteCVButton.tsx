"use client";

import { useRouter } from "next/navigation";
import { DeleteModeProvider } from "@/features/cv/context/DeleteModeContext";
import { DeleteCVDialog } from "./DeleteCVDialog";

interface DeleteCVButtonProps {
  cvId: string;
  filename: string;
  redirectTo?: string;
}

export function DeleteCVButton({
  cvId,
  filename,
  redirectTo = "/cvs",
}: DeleteCVButtonProps) {
  const router = useRouter();

  const handleDeleteSuccess = () => {
    router.push(redirectTo);
  };

  return (
    <DeleteModeProvider>
      <DeleteCVDialog
        cvId={cvId}
        filename={filename}
        onDeleteSuccess={handleDeleteSuccess}
      />
    </DeleteModeProvider>
  );
}
