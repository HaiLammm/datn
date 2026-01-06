import Link from "next/link";
import type { Metadata } from "next";
import { JobSearchPage } from "@/features/jobs/components/JobSearchPage";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Briefcase } from "lucide-react";

export const metadata: Metadata = {
    title: "Tìm kiếm việc làm - Jobs",
    description: "Tìm kiếm công việc phù hợp với bạn",
};

export default function FindJobsPage() {
    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <Link href="/">
                    <Button variant="ghost" size="icon" aria-label="Quay lại">
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                </Link>
                <div className="flex items-center gap-2">
                    <Briefcase className="h-6 w-6 text-primary" aria-hidden="true" />
                    <h1 className="text-2xl font-bold text-gray-900">
                        Tìm kiếm việc làm
                    </h1>
                </div>
            </div>

            {/* Description */}
            <p className="text-muted-foreground mb-6 max-w-2xl">
                Khám phá hàng ngàn cơ hội việc làm phù hợp với kỹ năng và kinh nghiệm của bạn.
                Tìm kiếm theo từ khóa và địa điểm để tìm công việc mơ ước.
            </p>

            {/* Search Content */}
            <JobSearchPage />
        </div>
    );
}
