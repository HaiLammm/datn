"use client";

import { CVWithStatus } from "@datn/shared-types";
import { CVHistoryList } from "./CVHistoryList";
import { DeleteModeProvider } from "@/features/cv/context/DeleteModeContext";

interface CVsClientWrapperProps {
  cvs: CVWithStatus[];
}

/**
 * Client wrapper component that provides delete mode context
 * and renders the CV history list.
 */
export function CVsClientWrapper({ cvs }: CVsClientWrapperProps) {
  return (
    <DeleteModeProvider>
      <CVHistoryList cvs={cvs} />
    </DeleteModeProvider>
  );
}
