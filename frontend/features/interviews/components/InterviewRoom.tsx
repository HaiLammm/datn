"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, CheckCircle2, Play, BookOpen, Clock } from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { InterviewSessionComplete, InterviewQuestion } from "@/features/interviews/types";
import { interviewService } from "@/services/interview.service";

interface InterviewRoomProps {
    initialSession: InterviewSessionComplete;
}

export function InterviewRoom({ initialSession }: InterviewRoomProps) {
    const router = useRouter();
    const [session, setSession] = useState<InterviewSessionComplete>(initialSession);
    const [hasStarted, setHasStarted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

    // Derive topics from questions
    const topics = Array.from(new Set(session.questions.map(q => q.category)));
    const difficulty = session.questions[0]?.difficulty || "Unknown";

    const handleStart = () => {
        setHasStarted(true);
    };

    const currentQuestion = session.questions[currentQuestionIndex];

    if (!hasStarted) {
        return (
            <div className="w-full max-w-2xl mx-auto space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-2xl">Ready for Interview</CardTitle>
                        <CardDescription>Your AI interviewer has prepared a personalized session for you.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="flex flex-col space-y-2 p-4 bg-muted/50 rounded-lg">
                                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                    <BookOpen className="h-4 w-4" /> Questions
                                </span>
                                <span className="text-2xl font-bold">{session.questions.length}</span>
                            </div>
                            <div className="flex flex-col space-y-2 p-4 bg-muted/50 rounded-lg">
                                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                    Level
                                </span>
                                <span className="text-2xl font-bold capitalize">{difficulty}</span>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <span className="text-sm font-medium">Focus Topics</span>
                            <div className="flex flex-wrap gap-2">
                                {topics.map(topic => (
                                    <Badge key={topic} variant="secondary" className="capitalize">
                                        {topic}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <span className="text-sm font-medium">Session Outline</span>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li className="flex items-center gap-2">
                                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    Introduction & Setup (Completed)
                                </li>
                                <li className="flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    Technical Questions ({session.questions.filter(q => q.category === 'technical').length})
                                </li>
                                <li className="flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    Behavioral/Situational Questions ({session.questions.filter(q => q.category !== 'technical').length})
                                </li>
                                <li className="flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    AI Evaluation & Feedback
                                </li>
                            </ul>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button size="lg" className="w-full" onClick={handleStart}>
                            <Play className="mr-2 h-4 w-4" /> Start Interview
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        );
    }

    // Active Interview View (Placeholder for Story 8.2/8.3, but showing first question as POC)
    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Question {currentQuestionIndex + 1} of {session.questions.length}</h2>
                <Badge variant="outline" className="capitalize">{currentQuestion.category}</Badge>
            </div>

            <Card className="min-h-[200px] flex items-center justify-center p-6 border-primary/20 bg-primary/5">
                <p className="text-lg font-medium text-center">
                    {currentQuestion.question_text}
                </p>
            </Card>

            {/* Chat Interface Placeholder */}
            <div className="p-8 border rounded-lg bg-muted/20 text-center text-muted-foreground">
                <p>Chat Interface will be implemented in Story 8.2</p>
                <Button variant="outline" className="mt-4" onClick={() => {
                    if (currentQuestionIndex < session.questions.length - 1) {
                        setCurrentQuestionIndex(prev => prev + 1);
                    } else {
                        alert("Interview Finished!");
                    }
                }}>
                    Next Question (Demo)
                </Button>
            </div>
        </div>
    );
}
