import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import { getJDAction, getCandidateCVAction } from "@/features/jobs/actions";
import Link from "next/link";
import { ArrowLeft, Lock, FileText, Briefcase, Award, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScoreGauge } from "@/features/cv/components/ScoreGauge";
import { SkillCloud } from "@/features/cv/components/SkillCloud";
import { SkillCategoriesDisplay } from "@/features/cv/components/SkillCategoriesDisplay";
import { SkillBreakdownCard } from "@/features/cv/components/SkillBreakdownCard";
import { SkillBreakdown, SkillCategories } from "@datn/shared-types";
import { PDFPreviewSection } from "./PDFPreviewSection";

interface CandidateCVPageProps {
  params: Promise<{
    jdId: string;
    cvId: string;
  }>;
}

export default async function CandidateCVPage({ params }: CandidateCVPageProps) {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const { jdId, cvId } = await params;

  // Fetch JD details (for title and navigation)
  const jd = await getJDAction(jdId);

  // 404 if JD not found or not owner
  if (!jd) {
    notFound();
  }

  // Fetch CV details
  const result = await getCandidateCVAction(jdId, cvId);

  // Handle error cases
  if (!result.success) {
    if (result.errorCode === "PRIVATE") {
      return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <Link
            href={`/jobs/jd/${jdId}/candidates`}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-6"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lai danh sach ung vien
          </Link>

          <Card className="p-8 text-center">
            <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              CV la rieng tu
            </h1>
            <p className="text-muted-foreground mb-4">
              Ung vien nay da chon giu CV cua ho o che do rieng tu. Ban chi co the xem diem phu hop va ky nang da so khop.
            </p>
            <p className="text-sm text-muted-foreground">
              Ung vien co the chon cong khai CV cua ho trong tuong lai.
            </p>
          </Card>
        </div>
      );
    }

    if (result.errorCode === "NOT_FOUND") {
      notFound();
    }

    // Unknown error
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Link
          href={`/jobs/jd/${jdId}/candidates`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Quay lai danh sach ung vien
        </Link>

        <Card className="p-8 text-center">
          <h1 className="text-xl font-semibold text-red-600 mb-2">
            Da xay ra loi
          </h1>
          <p className="text-muted-foreground mb-4">
            {result.error || "Khong the tai thong tin CV. Vui long thu lai sau."}
          </p>
          <Link href={`/jobs/jd/${jdId}/candidates`}>
            <Button variant="outline">Quay lai</Button>
          </Link>
        </Card>
      </div>
    );
  }

  const cvData = result.data!;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-6">
        <Link
          href={`/jobs/jd/${jdId}/candidates`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Quay lai danh sach ung vien
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <FileText className="h-6 w-6 text-gray-400" />
              {cvData.filename}
            </h1>
            <p className="text-muted-foreground mt-1">
              Ung vien cho &quot;{jd.title}&quot;
            </p>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="flex gap-6">
        {/* Left Column - Analysis Data */}
        <div className="flex-1 min-w-0">
          {/* Match Context Section */}
          {cvData.match_score !== null && (
            <Card className="p-6 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-blue-600" />
                Do phu hop voi JD
              </h2>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">
                    {cvData.match_score}%
                  </div>
                  <div className="text-sm text-gray-500">Diem phu hop</div>
                </div>
                {cvData.matched_skills && cvData.matched_skills.length > 0 && (
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      Ky nang phu hop ({cvData.matched_skills.length})
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {cvData.matched_skills.map((skill, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* CV Quality Score */}
          {cvData.ai_score !== null && (
            <Card className="p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Award className="h-5 w-5 text-yellow-500" />
                Diem chat luong CV
              </h2>
              <ScoreGauge score={cvData.ai_score} />
            </Card>
          )}

          {/* Summary Section */}
          {cvData.ai_summary && (
            <Card className="p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Tom tat chuyen mon
              </h2>
              <p className="text-gray-700 leading-relaxed">{cvData.ai_summary}</p>
            </Card>
          )}

          {/* Skill Breakdown Section */}
          {cvData.skill_breakdown && (
            <Card className="p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Phan tich ky nang
              </h2>
              <SkillBreakdownCard breakdown={cvData.skill_breakdown as unknown as SkillBreakdown} />
            </Card>
          )}

          {/* Skills Section */}
          {(cvData.skill_categories || cvData.extracted_skills) && (
            <Card className="p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {cvData.skill_categories ? "Phan loai ky nang" : "Ky nang da trich xuat"}
              </h2>
              {cvData.skill_categories ? (
                <SkillCategoriesDisplay categories={cvData.skill_categories as unknown as SkillCategories} />
              ) : (
                <SkillCloud skills={cvData.extracted_skills || []} />
              )}
            </Card>
          )}

          {/* Upload Info */}
          <div className="text-center text-sm text-muted-foreground mt-8">
            CV duoc tai len: {new Date(cvData.uploaded_at).toLocaleDateString("vi-VN", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </div>
        </div>

        {/* Right Column - PDF Preview (Sticky) */}
        <div className="w-[500px] flex-shrink-0">
          <div className="sticky top-4">
            <PDFPreviewSection
              jdId={jdId}
              cvId={cvId}
              filename={cvData.filename}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
