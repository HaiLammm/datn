import { JDUploadForm } from "@/features/jobs/components/JDUploadForm";
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default async function JDUploadPage() {
  // Authentication Guard
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  if (session.user.role !== 'recruiter' && session.user.role !== 'admin') {
    redirect("/jobs/find");
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <Link
          href="/jobs"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Quay lại danh sách JD
        </Link>
      </div>

      <JDUploadForm />
    </div>
  );
}
