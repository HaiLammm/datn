import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar, DollarSign, Briefcase } from "lucide-react";
import Link from "next/link";

interface JobCardProps {
    id: string;
    title: string;
    description: string;
    location_type: string;
    uploaded_at: string;
    salary_min?: number;
    salary_max?: number;
    job_type?: string;
}

const locationTypeLabels: Record<string, string> = {
    remote: "Remote",
    hybrid: "Hybrid",
    "on-site": "Tại văn phòng",
};

const locationTypeColors: Record<string, string> = {
    remote: "bg-green-100 text-green-800 hover:bg-green-200",
    hybrid: "bg-blue-100 text-blue-800 hover:bg-blue-200",
    "on-site": "bg-purple-100 text-purple-800 hover:bg-purple-200",
};

const jobTypeLabels: Record<string, string> = {
    "full-time": "Full-time",
    "part-time": "Part-time",
    "contract": "Contract",
    "internship": "Internship",
    "freelance": "Freelance",
};

export function JobCard({
    id,
    title,
    description,
    location_type,
    uploaded_at,
    salary_min,
    salary_max,
    job_type,
}: JobCardProps) {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return "Hôm nay";
        if (diffDays === 1) return "Hôm qua";
        if (diffDays < 7) return `${diffDays} ngày trước`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} tuần trước`;
        return date.toLocaleDateString("vi-VN");
    };

    const formatSalary = (min?: number, max?: number) => {
        if (!min && !max) return null;
        if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} VNĐ`;
        if (min) return `Từ ${min.toLocaleString()} VNĐ`;
        if (max) return `Lên đến ${max.toLocaleString()} VNĐ`;
    };

    const salary = formatSalary(salary_min, salary_max);

    return (
        <Link href={`/jobs/${id}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                            <CardTitle className="text-xl mb-2 line-clamp-2">{title}</CardTitle>
                            <CardDescription className="line-clamp-3">{description}</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                        {/* Location Type */}
                        <div className="flex items-center gap-1.5">
                            <MapPin className="h-4 w-4" />
                            <Badge
                                variant="secondary"
                                className={locationTypeColors[location_type] || ""}
                            >
                                {locationTypeLabels[location_type] || location_type}
                            </Badge>
                        </div>

                        {/* Job Type */}
                        {job_type && (
                            <div className="flex items-center gap-1.5">
                                <Briefcase className="h-4 w-4" />
                                <span className="capitalize">{jobTypeLabels[job_type] || job_type}</span>
                            </div>
                        )}

                        {/* Posted Date */}
                        <div className="flex items-center gap-1.5">
                            <Calendar className="h-4 w-4" />
                            <span>{formatDate(uploaded_at)}</span>
                        </div>

                        {/* Salary */}
                        {salary && (
                            <div className="flex items-center gap-1.5">
                                <DollarSign className="h-4 w-4" />
                                <span className="font-medium text-foreground">{salary}</span>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}
