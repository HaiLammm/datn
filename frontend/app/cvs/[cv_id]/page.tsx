import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import { getCVAnalysis } from "@/features/cv/actions";
import { CVAnalysisResults } from "@/features/cv/components/CVAnalysisResults";

interface CVAnalysisPageProps {
  params: Promise<{ cv_id: string }>;
}

export default async function CVAnalysisPage({ params }: CVAnalysisPageProps) {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const { cv_id } = await params;

  try {
    const analysis = await getCVAnalysis(cv_id);

    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <a
            href="/cvs"
            className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block"
          >
            &larr; Back to My CVs
          </a>
          <h1 className="text-3xl font-bold text-gray-900">
            CV Analysis Results
          </h1>
        </div>

        <CVAnalysisResults cvId={cv_id} initialAnalysis={analysis} />
      </div>
    );
  } catch (error) {
    console.error("Error loading analysis:", error);
    notFound();
  }
}
