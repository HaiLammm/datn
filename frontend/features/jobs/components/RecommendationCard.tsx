import React from "react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { JobRecommendation } from "@datn/shared-types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MapPin, DollarSign, Clock, Briefcase, Zap, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface RecommendationCardProps {
    job: JobRecommendation;
    className?: string;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ job, className }) => {
    // Color coding for match score
    const getScoreColor = (score: number) => {
        if (score >= 80) return "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800";
        if (score >= 60) return "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800";
        return "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800";
    };

    const scoreColorClass = getScoreColor(job.match_score);

    return (
        <Card className={cn("flex flex-col h-full hover:shadow-lg transition-shadow border-l-4", className)}
            style={{ borderLeftColor: job.match_score >= 80 ? '#22c55e' : job.match_score >= 60 ? '#3b82f6' : '#eab308' }}>
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start gap-4">
                    <div>
                        <CardTitle className="text-xl font-bold line-clamp-2 hover:text-primary transition-colors">
                            <Link href={`/jobs/${job.id}`}>
                                {job.title}
                            </Link>
                        </CardTitle>
                        <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                                <MapPin className="h-3.5 w-3.5" />
                                {job.location_type === 'remote' ? 'Remote' : job.location_type === 'hybrid' ? 'Hybrid' : 'On-site'}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                                <Clock className="h-3.5 w-3.5" />
                                {formatDistanceToNow(new Date(job.uploaded_at), { addSuffix: true })}
                            </span>
                        </div>
                    </div>

                    <div className={cn("flex flex-col items-center justify-center p-2 rounded-lg border", scoreColorClass)}>
                        <span className="text-2xl font-bold">{job.match_score}%</span>
                        <span className="text-xs font-medium uppercase tracking-wider">Match</span>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="flex-grow pb-2">
                <div className="space-y-4">
                    {/* Salary info */}
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        {job.salary_min && job.salary_max
                            ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
                            : job.salary_min
                                ? `From $${job.salary_min.toLocaleString()}`
                                : "Salary Negotiable"}
                    </div>

                    {/* Description Snippet */}
                    <p className="text-sm text-muted-foreground line-clamp-2">
                        {job.description}
                    </p>

                    {/* Key Skill Matches */}
                    {job.matched_skills.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
                                <Zap className="h-3 w-3" />
                                Top Matched Skills
                            </p>
                            <div className="flex flex-wrap gap-1.5">
                                {job.matched_skills.slice(0, 3).map((skill, i) => (
                                    <Badge key={i} variant="secondary" className="px-1.5 py-0 text-xs bg-green-50 text-green-700 hover:bg-green-100 border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900">
                                        <CheckCircle2 className="h-3 w-3 mr-1" />
                                        {skill}
                                    </Badge>
                                ))}
                                {job.matched_skills.length > 3 && (
                                    <span className="text-xs text-muted-foreground px-1 py-0.5">+{job.matched_skills.length - 3} more</span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Missing Skills (only if high match but missing some key things) */}
                    {job.missing_skills.length > 0 && job.match_score < 100 && (
                        <div className="space-y-2">
                            <p className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
                                <Briefcase className="h-3 w-3" />
                                Missing Key Skills
                            </p>
                            <div className="flex flex-wrap gap-1.5">
                                {job.missing_skills.slice(0, 2).map((skill, i) => (
                                    <Badge key={i} variant="outline" className="px-1.5 py-0 text-xs text-muted-foreground">
                                        <XCircle className="h-3 w-3 mr-1 text-muted-foreground" />
                                        {skill}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>

            <CardFooter className="pt-2">
                <Button asChild className="w-full" variant={job.match_score >= 80 ? "default" : "secondary"}>
                    <Link href={`/jobs/${job.id}`}>
                        View Details
                    </Link>
                </Button>
            </CardFooter>
        </Card>
    );
};
