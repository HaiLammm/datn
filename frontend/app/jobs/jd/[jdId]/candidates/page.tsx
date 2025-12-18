import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import { getJDAction, getCandidatesAction } from "@/features/jobs/actions";
import { CandidateList } from "@/features/jobs/components/CandidateList";
import Link from "next/link";
import { ArrowLeft, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface CandidatesPageProps {
  params: Promise<{
    jdId: string;
  }>;
}

export default async function CandidatesPage({ params }: CandidatesPageProps) {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const { jdId } = await params;
  
  // Fetch JD details
  const jd = await getJDAction(jdId);

  // 404 if JD not found or not owner
  if (!jd) {
    notFound();
  }

  // Check if parsing is complete
  if (jd.parse_status !== "completed") {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Link
          href={`/jobs/jd/${jdId}`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Quay lại JD
        </Link>

        <Card className="p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            JD chưa sẵn sàng
          </h1>
          <p className="text-muted-foreground mb-4">
            {jd.parse_status === "pending" && "JD đang chờ phân tích. Vui lòng quay lại sau."}
            {jd.parse_status === "processing" && "JD đang được phân tích. Vui lòng quay lại sau vài phút."}
            {jd.parse_status === "failed" && "Phân tích JD thất bại. Vui lòng thử tải lại JD."}
          </p>
          <Link href={`/jobs/jd/${jdId}`}>
            <Button variant="outline">
              Xem chi tiết JD
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  // Fetch initial candidates data
  const initialCandidates = await getCandidatesAction(jdId, {
    limit: 20,
    offset: 0,
  });

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Link
          href={`/jobs/jd/${jdId}`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Quay lại JD
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">
          Ứng viên cho &quot;{jd.title}&quot;
        </h1>
        <p className="text-muted-foreground mt-1">
          Danh sách ứng viên được xếp hạng theo độ phù hợp với yêu cầu công việc
        </p>
      </div>

      {/* Candidate List */}
      <CandidateList
        jdId={jdId}
        initialData={initialCandidates || undefined}
      />
    </div>
  );
}
