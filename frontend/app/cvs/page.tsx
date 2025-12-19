import { Suspense } from "react";
import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getCVList } from "@/features/cv/actions";
import { CVsClientWrapper } from "@/features/cv/components/CVsClientWrapper";
import { CVHistorySkeleton } from "@/features/cv/components/CVHistorySkeleton";

export default async function CVsPage() {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const cvs = await getCVList();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My CVs</h1>
        <p className="text-gray-600">
          View and manage your uploaded CVs and their analysis results.
        </p>
      </div>

      <div className="mb-6">
        <Link
          href="/cvs/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Upload New CV
        </Link>
      </div>

      <Suspense fallback={<CVHistorySkeleton />}>
        <CVsClientWrapper cvs={cvs} />
      </Suspense>
    </div>
  );
}
