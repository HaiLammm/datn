import type { Metadata } from "next";
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import { JobSearchPage } from "@/features/jobs/components/JobSearchPage";
export const metadata: Metadata = {
    title: "Tìm kiếm việc làm - Jobs",
    description: "Tìm kiếm công việc phù hợp với bạn",
};

export default async function FindJobsPage() {
    const session = await getSession();

    if (!session) {
        redirect("/login?redirect=/jobs/find");
    }

    if (session.user.role !== "job_seeker") {
        redirect("/jobs");
    }

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <JobSearchPage />
            </div>
        </div>
    );
}
