"use client";

import { CVWithStatus } from "@datn/shared-types";
import Link from "next/link";
import { DeleteCVDialog } from "@/features/cv/components/DeleteCVDialog";
import {
  DeleteModeProvider,
  useDeleteMode,
} from "@/features/cv/context/DeleteModeContext";
import { Button } from "@/components/ui/button";

interface CVsClientWrapperProps {
  cvs: CVWithStatus[];
}

export function CVsClientWrapper({ cvs }: CVsClientWrapperProps) {
  return (
    <DeleteModeProvider>
      <CVsContent cvs={cvs} />
    </DeleteModeProvider>
  );
}

function CVsContent({ cvs }: { cvs: CVWithStatus[] }) {
  const { skipConfirmation, resetConfirmation } = useDeleteMode();

  if (cvs.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg
            className="mx-auto h-12 w-12"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No CVs uploaded yet
        </h3>
        <p className="text-gray-600 mb-6">
          Get started by uploading your first CV for analysis.
        </p>
        <Link
          href="/cvs/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Upload Your First CV
        </Link>
      </div>
    );
  }

  return (
    <>
      {skipConfirmation && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md flex items-center justify-between">
          <p className="text-sm text-yellow-800">
            Quick delete mode is enabled. CVs will be deleted without
            confirmation.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={resetConfirmation}
            className="ml-4 shrink-0"
          >
            Enable Confirmation
          </Button>
        </div>
      )}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {cvs.map((cv) => (
          <CVCard key={cv.id} cv={cv} />
        ))}
      </div>
    </>
  );
}

function CVCard({ cv }: { cv: CVWithStatus }) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Completed
          </span>
        );
      case "PROCESSING":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            Processing
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            Pending
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {cv.filename}
          </h3>
          <p className="text-sm text-gray-600">
            Uploaded {new Date(cv.uploaded_at).toLocaleDateString()}
          </p>
        </div>
        {getStatusBadge(cv.analysis_status)}
      </div>

      <div className="flex space-x-3">
        <Link
          href={`/cvs/${cv.id}/analysis`}
          className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          View Analysis
        </Link>
        <DeleteCVDialog cvId={cv.id} filename={cv.filename} />
      </div>
    </div>
  );
}
