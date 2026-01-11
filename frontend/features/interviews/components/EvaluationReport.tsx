"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { 
    CheckCircle2, 
    XCircle, 
    AlertTriangle, 
    TrendingUp, 
    TrendingDown,
    ChevronDown,
    ChevronUp,
    Award,
    Target,
    Lightbulb
} from "lucide-react";
import { useState } from "react";
import type { InterviewSessionComplete, InterviewEvaluationResponse } from "../types";

interface EvaluationReportProps {
    session: InterviewSessionComplete;
    evaluation: InterviewEvaluationResponse;
}

export function EvaluationReport({ session, evaluation }: EvaluationReportProps) {
    const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
        technical: true,
        communication: false,
        behavioral: false,
    });

    const toggleSection = (section: string) => {
        setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
    };

    // Helper functions
    const getGradeColor = (grade: string) => {
        switch (grade.toLowerCase()) {
            case "excellent":
            case "a":
                return "bg-green-500";
            case "good":
            case "b":
                return "bg-blue-500";
            case "average":
            case "c":
                return "bg-yellow-500";
            case "poor":
            case "d":
            case "f":
                return "bg-red-500";
            default:
                return "bg-gray-500";
        }
    };

    const getRecommendationIcon = (recommendation: string) => {
        const rec = recommendation.toLowerCase();
        if (rec.includes("strong") || rec.includes("hire")) return <CheckCircle2 className="h-5 w-5 text-green-500" />;
        if (rec.includes("consider")) return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
        return <XCircle className="h-5 w-5 text-red-500" />;
    };

    const getScoreColor = (score: number) => {
        if (score >= 8) return "text-green-600";
        if (score >= 6) return "text-blue-600";
        if (score >= 4) return "text-yellow-600";
        return "text-red-600";
    };

    // Extract dimension scores with fallbacks
    const dimensions = [
        {
            key: "technical",
            title: "Technical Competency",
            data: evaluation.dimension_scores.technical_competency || evaluation.dimension_scores.technical_competence,
            icon: Target
        },
        {
            key: "communication",
            title: "Communication Skills",
            data: evaluation.dimension_scores.communication_skills,
            icon: TrendingUp
        },
        {
            key: "behavioral",
            title: "Behavioral Fit",
            data: evaluation.dimension_scores.behavioral_fit,
            icon: Award
        }
    ].filter(d => d.data); // Only show dimensions that have data

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Interview Evaluation Report</h1>
                    <p className="text-muted-foreground">
                        Interview completed on {new Date(session.completed_at || "").toLocaleDateString()}
                    </p>
                </div>
                <Badge className={getGradeColor(evaluation.grade)} variant="default">
                    Grade: {evaluation.grade.toUpperCase()}
                </Badge>
            </div>

            {/* Overall Score Section */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        <span>Overall Performance</span>
                        <span className={`text-4xl font-bold ${getScoreColor(evaluation.final_score)}`}>
                            {evaluation.final_score.toFixed(1)}/10
                        </span>
                    </CardTitle>
                    <CardDescription>Final evaluation score and hiring recommendation</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <Progress value={evaluation.final_score * 10} className="h-3" />
                    
                    <Alert>
                        <div className="flex items-center gap-2">
                            {getRecommendationIcon(evaluation.hiring_recommendation)}
                            <AlertDescription className="font-semibold">
                                Hiring Recommendation: {evaluation.hiring_recommendation.replace(/_/g, " ").toUpperCase()}
                            </AlertDescription>
                        </div>
                    </Alert>
                </CardContent>
            </Card>

            {/* Dimension Scores Breakdown */}
            <Card>
                <CardHeader>
                    <CardTitle>Performance Dimensions</CardTitle>
                    <CardDescription>Detailed breakdown across key evaluation areas</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {dimensions.map((dimension) => {
                        if (!dimension.data) return null;
                        const Icon = dimension.icon;
                        
                        return (
                            <Collapsible
                                key={dimension.key}
                                open={expandedSections[dimension.key]}
                                onOpenChange={() => toggleSection(dimension.key)}
                            >
                                <Card>
                                    <CollapsibleTrigger className="w-full">
                                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                            <div className="flex items-center gap-2">
                                                <Icon className="h-5 w-5" />
                                                <CardTitle className="text-lg">{dimension.title}</CardTitle>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <span className={`text-2xl font-bold ${getScoreColor(dimension.data.score)}`}>
                                                    {dimension.data.score.toFixed(1)}
                                                </span>
                                                <span className="text-sm text-muted-foreground">
                                                    (Weight: {(dimension.data.weight * 100).toFixed(0)}%)
                                                </span>
                                                {expandedSections[dimension.key] ? 
                                                    <ChevronUp className="h-4 w-4" /> : 
                                                    <ChevronDown className="h-4 w-4" />
                                                }
                                            </div>
                                        </CardHeader>
                                    </CollapsibleTrigger>
                                    
                                    <CollapsibleContent>
                                        <CardContent className="space-y-4">
                                            {/* Sub-scores */}
                                            <div>
                                                <h4 className="font-semibold mb-2">Sub-dimension Scores:</h4>
                                                <div className="grid grid-cols-2 gap-3">
                                                    {Object.entries(dimension.data.sub_scores).map(([key, value]) => (
                                                        <div key={key} className="flex items-center justify-between">
                                                            <span className="text-sm capitalize">
                                                                {key.replace(/_/g, " ")}
                                                            </span>
                                                            <span className={`font-semibold ${getScoreColor(value as number)}`}>
                                                                {(value as number).toFixed(1)}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Evidence */}
                                            {dimension.data.evidence && dimension.data.evidence.length > 0 && (
                                                <div>
                                                    <h4 className="font-semibold mb-2">Evidence from Interview:</h4>
                                                    <ul className="space-y-2">
                                                        {dimension.data.evidence.map((item, idx) => (
                                                            <li key={idx} className="text-sm text-muted-foreground italic border-l-2 pl-3">
                                                                "{item}"
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {/* Analysis */}
                                            {dimension.data.analysis && (
                                                <div>
                                                    <h4 className="font-semibold mb-2">Analysis:</h4>
                                                    <p className="text-sm text-muted-foreground">{dimension.data.analysis}</p>
                                                </div>
                                            )}
                                        </CardContent>
                                    </CollapsibleContent>
                                </Card>
                            </Collapsible>
                        );
                    })}
                </CardContent>
            </Card>

            {/* Detailed Analysis */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Strengths */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-green-500" />
                            Key Strengths
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {(evaluation.detailed_analysis.key_strengths || evaluation.detailed_analysis.strengths || []).map((strength, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                    <span className="text-sm">{strength}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>

                {/* Areas for Improvement */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingDown className="h-5 w-5 text-yellow-500" />
                            Areas for Improvement
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {(evaluation.detailed_analysis.areas_for_improvement || evaluation.detailed_analysis.weaknesses || []).map((area, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                    <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                                    <span className="text-sm">{area}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </div>

            {/* Notable Moments */}
            {evaluation.detailed_analysis.notable_moments && evaluation.detailed_analysis.notable_moments.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Lightbulb className="h-5 w-5 text-blue-500" />
                            Notable Moments
                        </CardTitle>
                        <CardDescription>Highlights from the interview</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-3">
                            {evaluation.detailed_analysis.notable_moments.map((moment, idx) => (
                                <li key={idx} className="text-sm border-l-2 border-blue-500 pl-3">
                                    {moment}
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}

            {/* Red Flags */}
            {evaluation.detailed_analysis.red_flags && evaluation.detailed_analysis.red_flags.length > 0 && (
                <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                        <p className="font-semibold mb-2">Red Flags Identified:</p>
                        <ul className="space-y-1">
                            {evaluation.detailed_analysis.red_flags.map((flag, idx) => (
                                <li key={idx}>• {flag}</li>
                            ))}
                        </ul>
                    </AlertDescription>
                </Alert>
            )}

            {/* Recommendations */}
            <Card>
                <CardHeader>
                    <CardTitle>Hiring Decision & Recommendations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="font-semibold mb-2">Decision:</h4>
                        <p className="text-sm">{evaluation.recommendations.hiring_decision}</p>
                    </div>
                    
                    <div>
                        <h4 className="font-semibold mb-2">Reasoning:</h4>
                        <p className="text-sm text-muted-foreground">{evaluation.recommendations.reasoning}</p>
                    </div>

                    {evaluation.recommendations.role_fit && (
                        <div>
                            <h4 className="font-semibold mb-2">Role Fit Assessment:</h4>
                            <p className="text-sm text-muted-foreground">{evaluation.recommendations.role_fit}</p>
                        </div>
                    )}

                    {(evaluation.recommendations.development_areas || evaluation.recommendations.development_suggestions) && (
                        <div>
                            <h4 className="font-semibold mb-2">Development Suggestions:</h4>
                            <ul className="space-y-1">
                                {(evaluation.recommendations.development_areas || evaluation.recommendations.development_suggestions || []).map((suggestion, idx) => (
                                    <li key={idx} className="text-sm text-muted-foreground">• {suggestion}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {evaluation.recommendations.onboarding_suggestions && evaluation.recommendations.onboarding_suggestions.length > 0 && (
                        <div>
                            <h4 className="font-semibold mb-2">Onboarding Suggestions:</h4>
                            <ul className="space-y-1">
                                {evaluation.recommendations.onboarding_suggestions.map((suggestion, idx) => (
                                    <li key={idx} className="text-sm text-muted-foreground">• {suggestion}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Metadata */}
            {evaluation.evaluation_metadata && (
                <Card>
                    <CardHeader>
                        <CardTitle>Interview Statistics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            {evaluation.evaluation_metadata.total_questions && (
                                <div>
                                    <p className="text-muted-foreground">Total Questions</p>
                                    <p className="font-semibold">{evaluation.evaluation_metadata.total_questions}</p>
                                </div>
                            )}
                            {evaluation.evaluation_metadata.interview_duration && (
                                <div>
                                    <p className="text-muted-foreground">Duration</p>
                                    <p className="font-semibold">{evaluation.evaluation_metadata.interview_duration} mins</p>
                                </div>
                            )}
                            {evaluation.evaluation_metadata.model_used && (
                                <div>
                                    <p className="text-muted-foreground">AI Model</p>
                                    <p className="font-semibold text-xs">{evaluation.evaluation_metadata.model_used}</p>
                                </div>
                            )}
                            <div>
                                <p className="text-muted-foreground">Evaluated On</p>
                                <p className="font-semibold text-xs">{new Date(evaluation.created_at).toLocaleString()}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
