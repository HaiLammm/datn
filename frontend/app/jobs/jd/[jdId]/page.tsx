import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import { getJDAction } from "@/features/jobs/actions";
import { JDDetailClient } from "@/features/jobs/components/JDDetailClient";

interface JDDetailPageProps {
  params: Promise<{
    jdId: string;
  }>;
}

export default async function JDDetailPage({ params }: JDDetailPageProps) {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const { jdId } = await params;
  const jd = await getJDAction(jdId);

  // 404 if JD not found or not owner
  if (!jd) {
    notFound();
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <JDDetailClient jd={jd} />
    </div>
  );
}
