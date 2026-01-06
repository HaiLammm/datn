import { jobService } from "@/services/job.service";
import { JobDetailClient } from "@/features/jobs/components/JobDetailClient";
import { notFound } from "next/navigation";
import { Metadata } from "next";

interface PageProps {
    params: Promise<{
        id: string;
    }>;
}

export async function generateMetadata(props: PageProps): Promise<Metadata> {
    try {
        const params = await props.params;
        const job = await jobService.getJobDetail(params.id);
        return {
            title: `${job.title} | AI Recruitment`,
            description: job.description.substring(0, 160),
        };
    } catch {
        return {
            title: "Job Not Found",
        };
    }
}

export default async function JobDetailPage(props: PageProps) {
    const params = await props.params;
    try {
        const job = await jobService.getJobDetail(params.id);
        return <JobDetailClient job={job} />;
    } catch (error: any) {
        console.error("Error fetching job detail:", error);

        // Chỉ gọi notFound() nếu đúng là lỗi 404 từ Backend
        if (error.response && error.response.status === 404) {
            notFound();
        }

        throw error;
    }
}
