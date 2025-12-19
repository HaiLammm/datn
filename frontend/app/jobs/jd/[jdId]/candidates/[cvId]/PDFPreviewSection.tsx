"use client";

import { useState } from "react";
import { Eye, FileText, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DownloadButton } from "@/components/common/DownloadButton";
import { jobService } from "@/services/job.service";

interface PDFPreviewSectionProps {
  jdId: string;
  cvId: string;
  filename: string;
}

export function PDFPreviewSection({ jdId, cvId, filename }: PDFPreviewSectionProps) {
  const [previewError, setPreviewError] = useState(false);

  const fileUrl = jobService.getCandidateCVFileUrl(jdId, cvId);
  const downloadUrl = `${fileUrl}?download=true`;

  const handleOpenInNewTab = () => {
    window.open(fileUrl, "_blank");
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Ho so goc
        </h2>
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="sm"
            onClick={handleOpenInNewTab}
            className="flex items-center gap-1 text-xs px-2"
          >
            <ExternalLink className="h-3 w-3" />
            Tab moi
          </Button>
          <DownloadButton
            downloadUrl={downloadUrl}
            filename={filename}
            variant="button"
            size="sm"
            buttonText="Tai xuong"
            loadingText="..."
            successMessage=""
            className="text-xs px-2"
            errorMessages={{
              403: "CV nay khong cong khai",
              404: "Khong tim thay CV",
            }}
          />
        </div>
      </div>

      {/* PDF Embed - Full height */}
      <div className="border rounded-lg overflow-hidden bg-gray-100">
        {!previewError ? (
          <embed
            src={fileUrl}
            type="application/pdf"
            className="w-full"
            style={{ height: "calc(100vh - 180px)" }}
            onError={() => setPreviewError(true)}
          />
        ) : (
          <div className="w-full flex flex-col items-center justify-center text-gray-500 py-20">
            <Eye className="h-10 w-10 mb-3 text-gray-400" />
            <p className="text-center text-sm mb-2">
              Khong the hien thi ban xem truoc PDF.
            </p>
            <p className="text-xs text-gray-400 mb-3">
              Trinh duyet co the khong ho tro.
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleOpenInNewTab}>
                <ExternalLink className="h-3 w-3 mr-1" />
                Mo tab moi
              </Button>
              <DownloadButton
                downloadUrl={downloadUrl}
                filename={filename}
                variant="button"
                size="sm"
                buttonText="Tai xuong"
                successMessage=""
                errorMessages={{
                  403: "CV nay khong cong khai",
                  404: "Khong tim thay CV",
                }}
              />
            </div>
          </div>
        )}
      </div>

      <p className="text-xs text-muted-foreground mt-2 text-center truncate">
        {filename}
      </p>
    </Card>
  );
}
