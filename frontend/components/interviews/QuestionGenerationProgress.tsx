"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, CheckCircle2, XCircle, Clock, Sparkles } from "lucide-react";

export type GenerationStatus = 'pending' | 'generating' | 'ready' | 'error';

interface QuestionGenerationProgressProps {
    status: GenerationStatus;
    errorMessage?: string;
    elapsedTime?: number;
    estimatedTimeRemaining?: number;
    onCancel?: () => void;
}

const statusConfig = {
    pending: {
        icon: Clock,
        color: "text-blue-500",
        bgColor: "bg-blue-50",
        title: "Preparing Interview",
        description: "Setting up AI agents and analyzing your requirements...",
        progress: 10,
    },
    generating: {
        icon: Sparkles,
        color: "text-purple-500",
        bgColor: "bg-purple-50",
        title: "Generating Questions",
        description: "AI is creating personalized interview questions based on the job description and CV...",
        progress: 50,
    },
    ready: {
        icon: CheckCircle2,
        color: "text-green-500",
        bgColor: "bg-green-50",
        title: "Questions Ready!",
        description: "Your interview questions have been successfully generated.",
        progress: 100,
    },
    error: {
        icon: XCircle,
        color: "text-red-500",
        bgColor: "bg-red-50",
        title: "Generation Failed",
        description: "Something went wrong while generating questions.",
        progress: 0,
    },
};

export function QuestionGenerationProgress({
    status,
    errorMessage,
    elapsedTime = 0,
    estimatedTimeRemaining,
    onCancel,
}: QuestionGenerationProgressProps) {
    const [animatedProgress, setAnimatedProgress] = useState(0);
    const config = statusConfig[status];
    const Icon = config.icon;

    // Smooth progress animation
    useEffect(() => {
        if (status === 'generating') {
            // Simulate gradual progress between 10% and 90%
            const interval = setInterval(() => {
                setAnimatedProgress((prev) => {
                    if (prev >= 90) return 90; // Cap at 90% until actually ready
                    return Math.min(prev + 1, 90);
                });
            }, 1500); // Increment every 1.5 seconds

            return () => clearInterval(interval);
        } else {
            setAnimatedProgress(config.progress);
        }
    }, [status, config.progress]);

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const isLoading = status === 'pending' || status === 'generating';

    return (
        <Card className={`w-full max-w-2xl mx-auto ${config.bgColor}`}>
            <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                    <div className={`rounded-full p-3 ${isLoading ? 'animate-pulse' : ''}`}>
                        <Icon className={`h-12 w-12 ${config.color} ${isLoading ? 'animate-spin-slow' : ''}`} />
                    </div>
                </div>
                <CardTitle className="text-2xl">{config.title}</CardTitle>
                <CardDescription className="text-base mt-2">
                    {config.description}
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Progress</span>
                        <span>{Math.round(animatedProgress)}%</span>
                    </div>
                    <Progress value={animatedProgress} className="h-2" />
                </div>

                {/* Time Information */}
                {isLoading && (
                    <div className="flex justify-between items-center text-sm">
                        <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">
                                Elapsed: <span className="font-medium text-foreground">{formatTime(elapsedTime)}</span>
                            </span>
                        </div>
                        {estimatedTimeRemaining !== undefined && (
                            <span className="text-muted-foreground">
                                Est. remaining: <span className="font-medium text-foreground">{formatTime(estimatedTimeRemaining)}</span>
                            </span>
                        )}
                    </div>
                )}

                {/* Status Messages */}
                {status === 'generating' && (
                    <Alert className="border-purple-200 bg-purple-50">
                        <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
                        <AlertDescription className="text-purple-800">
                            <div className="space-y-1">
                                <p className="font-medium">AI is working on:</p>
                                <ul className="list-disc list-inside space-y-1 text-sm">
                                    <li>Analyzing job requirements and technical skills</li>
                                    <li>Evaluating candidate's background and experience</li>
                                    <li>Creating personalized interview questions</li>
                                    <li>Generating evaluation criteria and key points</li>
                                </ul>
                            </div>
                        </AlertDescription>
                    </Alert>
                )}

                {status === 'pending' && (
                    <Alert className="border-blue-200 bg-blue-50">
                        <Clock className="h-4 w-4 text-blue-600" />
                        <AlertDescription className="text-blue-800">
                            Your request is queued. This typically takes 2-3 minutes depending on server load.
                        </AlertDescription>
                    </Alert>
                )}

                {status === 'error' && errorMessage && (
                    <Alert variant="destructive">
                        <XCircle className="h-4 w-4" />
                        <AlertDescription>
                            <p className="font-medium mb-1">Error Details:</p>
                            <p className="text-sm">{errorMessage}</p>
                            <p className="text-sm mt-2">
                                Please try again or contact support if the issue persists.
                            </p>
                        </AlertDescription>
                    </Alert>
                )}

                {status === 'ready' && (
                    <Alert className="border-green-200 bg-green-50">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <AlertDescription className="text-green-800">
                            Interview questions are ready! You can now proceed to start the interview.
                        </AlertDescription>
                    </Alert>
                )}

                {/* Cancel Button */}
                {isLoading && onCancel && (
                    <div className="flex justify-center">
                        <button
                            onClick={onCancel}
                            className="text-sm text-muted-foreground hover:text-foreground underline transition-colors"
                        >
                            Cancel generation
                        </button>
                    </div>
                )}

                {/* Tips */}
                {isLoading && (
                    <div className="text-xs text-muted-foreground text-center pt-4 border-t">
                        💡 Tip: Generation time depends on the number of questions and AI model response time.
                        Typically takes 2-3 minutes for 10 questions.
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

// Helper hook for tracking elapsed time
export function useElapsedTime(isRunning: boolean): number {
    const [elapsedTime, setElapsedTime] = useState(0);

    useEffect(() => {
        if (!isRunning) {
            setElapsedTime(0);
            return;
        }

        const startTime = Date.now();
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);

        return () => clearInterval(interval);
    }, [isRunning]);

    return elapsedTime;
}
