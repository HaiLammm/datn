import React from "react";
import Link from "next/link";
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import { RecommendationsList } from "@/features/jobs/components/RecommendationsList";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles, Filter } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export default async function RecommendationsPage() {
    const session = await getSession();

    if (!session) {
        redirect("/login?redirect=/jobs/recommendations");
    }

    if (session.user.role !== 'job_seeker') {
        redirect("/jobs");
    }

    return (
        <div className="container mx-auto py-8">
            <div className="flex items-center gap-2 mb-6 text-muted-foreground hover:text-foreground transition-colors w-fit">
                <Button variant="ghost" size="sm" asChild className="pl-0 gap-1">
                    <Link href="/jobs">
                        <ArrowLeft className="h-4 w-4" />
                        Back to Jobs
                    </Link>
                </Button>
            </div>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                        <span className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg text-white shadow-md inline-flex">
                            <Sparkles className="h-6 w-6" />
                        </span>
                        Recommended Jobs
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Personalized matches based on your skills, experience, and preferences.
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="hidden md:flex gap-2">
                        <Filter className="h-4 w-4" />
                        Filter Results
                    </Button>
                </div>
            </div>

            <Separator className="mb-8" />

            <RecommendationsList user={session.user} />
        </div>
    );
}
