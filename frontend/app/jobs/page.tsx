import { Suspense } from "react";
import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getJDListAction } from "@/features/jobs/actions";
import { JDList } from "@/features/jobs/components/JDList";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default async function JobsPage() {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const jds = await getJDListAction();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Job Descriptions của bạn
          </h1>
          <p className="text-gray-600">
            Quản lý và xem các Job Description đã tạo.
          </p>
        </div>

        <Link href="/jobs/jd/upload">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Tạo JD mới
          </Button>
        </Link>
      </div>

      <Suspense fallback={<JDsSkeleton />}>
        <JDList initialJDs={jds} />
      </Suspense>
    </div>
  );
}

function JDsSkeleton() {
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
              <div className="h-9 bg-gray-200 rounded w-10"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
