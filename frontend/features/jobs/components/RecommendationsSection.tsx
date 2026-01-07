"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { JobRecommendation, SessionUser } from "@datn/shared-types";
import { jobService } from "@/services/job.service";
import { RecommendationCard } from "./RecommendationCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ChevronRight, Sparkles, AlertCircle } from "lucide-react";

interface RecommendationsSectionProps {
    className?: string;
    limit?: number;
    user?: SessionUser | null;
}

export const RecommendationsSection: React.FC<RecommendationsSectionProps> = ({
    className,
    limit = 4,
    user
}) => {
    const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRecommendations = async () => {
            // Only fetch if user is a job seeker
            if (!user || user.role !== 'job_seeker') {
                setIsLoading(false);
                return;
            }

            try {
                setIsLoading(true);
                const data = await jobService.getRecommendations(limit);
                setRecommendations(data);
                setError(null);
            } catch (err) {
                console.error("Failed to load recommendations", err);
                setError("Failed to load recommendations");
            } finally {
                setIsLoading(false);
            }
        };

        fetchRecommendations();
    }, [user, limit]);

    // Don't render anything if not job seeker
    if (!user || user.role !== 'job_seeker') {
        return null;
    }

    return (
        <section className={className}>
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg text-white shadow-md">
                        <Sparkles className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Recommended for You</h2>
                        <p className="text-sm text-muted-foreground">
                            Jobs matching your skills and experience
                        </p>
                    </div>
                </div>

                {recommendations.length > 0 && (
                    <Button variant="ghost" className="group" asChild>
                        <Link href="/jobs/recommendations">
                            View All
                            <ChevronRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                    </Button>
                )}
            </div>

            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="space-y-3">
                            <Skeleton className="h-48 w-full rounded-xl" />
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-[250px]" />
                                <Skeleton className="h-4 w-[200px]" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : error ? (
                <div className="text-center py-8 text-muted-foreground">
                    Unable to load recommendations at this time.
                </div>
            ) : recommendations.length === 0 ? (
                <div className="flex items-start gap-4 p-4 border rounded-lg bg-muted/50 border-muted">
                    <AlertCircle className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div>
                        <h4 className="font-medium mb-1">No recommendations yet</h4>
                        <div className="text-sm text-muted-foreground">
                            Upload your CV to get personalized job matches tailored to your skills.
                            <div className="mt-3">
                                <Button asChild size="sm" variant="outline">
                                    <Link href="/profile/cv">Upload CV</Link>
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {recommendations.map((job) => (
                        <RecommendationCard key={job.id} job={job} />
                    ))}
                </div>
            )}
        </section>
    );
};
