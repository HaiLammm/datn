import { Suspense } from "react";
import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getCVList } from "@/features/cv/actions";
import { CVsClientWrapper } from "@/features/cv/components/CVsClientWrapper";

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

      <Suspense fallback={<CVsSkeleton />}>
        <CVsClientWrapper cvs={cvs} />
      </Suspense>
    </div>
  );
}

function CVsSkeleton() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
            </div>
            <div className="flex space-x-3">
              <div className="flex-1 h-9 bg-gray-200 rounded"></div>
              <div className="h-9 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
