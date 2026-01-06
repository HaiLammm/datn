"use client";

import { JobDescriptionResponse } from "@datn/shared-types";
import { format } from "date-fns";
import { MapPin, DollarSign, Calendar, Building, CheckCircle2, Briefcase } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ApplyJobDialog } from "./ApplyJobDialog";

interface JobDetailClientProps {
    job: JobDescriptionResponse;
}

export function JobDetailClient({ job }: JobDetailClientProps) {
    const formattedSalary = () => {
        if (job.salary_min && job.salary_max) {
            return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
        } else if (job.salary_min) {
            return `Từ $${job.salary_min.toLocaleString()}`;
        } else if (job.salary_max) {
            return `Lên tới $${job.salary_max.toLocaleString()}`;
        }
        return "Thỏa thuận";
    };

    const benefits = job.benefits || [];
    const skills = job.required_skills || [];

    // Mapping job types
    const jobTypeLabels: Record<string, string> = {
        "full-time": "Toàn thời gian",
        "part-time": "Bán thời gian",
        "contract": "Hợp đồng",
        "freelance": "Tự do",
        "internship": "Thực tập",
    };

    return (
        <div className="container mx-auto py-8 space-y-8">
            {/* Header Section */}
            <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
                <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
                        <div className="flex items-center gap-2 text-muted-foreground mt-2">
                            <Building className="w-4 h-4" />
                            <span>Công ty XYZ (Placeholder)</span>
                        </div>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-3">
                        <ApplyJobDialog job={job} />
                        <Button variant="outline" size="lg">Lưu tin</Button>
                    </div>
                </div>

                <div className="flex flex-wrap gap-4 pt-4 text-sm">
                    <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1.5 rounded-full">
                        <MapPin className="w-4 h-4 text-primary" />
                        <span className="capitalize">{job.location_type}</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1.5 rounded-full">
                        <DollarSign className="w-4 h-4 text-green-600" />
                        <span>{formattedSalary()}</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1.5 rounded-full">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                        <span>{jobTypeLabels[job.job_type || ""] || job.job_type || "Không xác định"}</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1.5 rounded-full">
                        <Calendar className="w-4 h-4 text-orange-600" />
                        <span>Đăng ngày {format(new Date(job.uploaded_at), "dd/MM/yyyy")}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Description */}
                    <section className="bg-white p-6 rounded-lg shadow-sm border">
                        <h2 className="text-xl font-bold mb-4">Mô tả công việc</h2>
                        <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                            {job.description}
                        </div>
                    </section>

                    {/* Requirements (Parsed or Description?) */}
                    {/* Using Parsed if available, else relying on Description text */}
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Skills */}
                    <section className="bg-white p-6 rounded-lg shadow-sm border">
                        <h2 className="text-lg font-bold mb-4">Kỹ năng yêu cầu</h2>
                        <div className="flex flex-wrap gap-2">
                            {skills.length > 0 ? skills.map(skill => (
                                <Badge key={skill} variant="secondary">{skill}</Badge>
                            )) : <span className="text-muted-foreground">Không yêu cầu cụ thể</span>}
                        </div>
                    </section>

                    {/* Benefits */}
                    <section className="bg-white p-6 rounded-lg shadow-sm border">
                        <h2 className="text-lg font-bold mb-4">Phúc lợi</h2>
                        <ul className="space-y-2">
                            {benefits.length > 0 ? benefits.map((benefit, index) => (
                                <li key={index} className="flex items-start gap-2">
                                    <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                                    <span className="text-sm">{benefit}</span> // Map key to label? Or just display text
                                </li>
                            )) : <span className="text-muted-foreground">Chưa cập nhật</span>}
                        </ul>
                    </section>
                </div>
            </div>
        </div>
    );
}
