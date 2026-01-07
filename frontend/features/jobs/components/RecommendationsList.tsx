"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { JobRecommendation, SessionUser } from "@datn/shared-types";
import { jobService } from "@/services/job.service";
import { RecommendationCard } from "./RecommendationCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { AlertCircle, Sparkles } from "lucide-react";

interface RecommendationsListProps {
    user: SessionUser;
    limit?: number;
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
    user,
    limit = 50
}) => {
    const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRecommendations = async () => {
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

    if (isLoading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="space-y-4">
                        <Skeleton className="h-64 w-full rounded-xl" />
                    </div>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12 text-muted-foreground">
                <p>Unable to load recommendations at this time.</p>
                <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
                    Try Again
                </Button>
            </div>
        );
    }

    if (recommendations.length === 0) {
        return (
            <div className="max-w-md mx-auto mt-12 text-center">
                <div className="bg-muted/50 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
                    <Sparkles className="h-10 w-10 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No recommendations found</h3>
                <p className="text-muted-foreground mb-6">
                    We couldn't find any jobs matching your profile right now.
                    Try updating your CV or skills to get better matches.
                </p>
                <div className="flex gap-4 justify-center">
                    <Button asChild>
                        <Link href="/profile/cv">Update CV</Link>
                    </Button>
                    <Button asChild variant="outline">
                        <Link href="/jobs">Browse All Jobs</Link>
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {recommendations.map((job) => (
                    <RecommendationCard key={job.id} job={job} />
                ))}
            </div>

            <div className="flex justify-center mt-12 text-muted-foreground text-sm">
                Showing top {recommendations.length} matches based on your profile
            </div>
        </div>
    );
};
