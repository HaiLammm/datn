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
import { generateNextQuestionAction } from "@/features/interviews/actions";
import { toast } from "sonner";

interface InterviewRoomProps {
    initialSession: InterviewSessionComplete;
}

export function InterviewRoom({ initialSession }: InterviewRoomProps) {
    const router = useRouter();
    const [session, setSession] = useState<InterviewSessionComplete>(initialSession);
    const [hasStarted, setHasStarted] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false);
    const [generatedQuestionCount, setGeneratedQuestionCount] = useState(initialSession.questions.length);

    // Derive topics from questions (only if questions exist)
    const topics = session.questions.length > 0 
        ? Array.from(new Set(session.questions.map(q => q.category)))
        : [];
    
    // Show position_level if no questions yet, otherwise show question difficulty
    const difficulty = session.questions.length > 0 
        ? (session.questions[0]?.difficulty || "medium")
        : (session.position_level || "medium");

    /**
     * Generate the next question on-demand.
     * Called when starting interview or after answering a question.
     */
    const generateNextQuestion = async () => {
        if (isGeneratingQuestion) return; // Prevent duplicate calls
        
        setIsGeneratingQuestion(true);
        toast.info("Generating next question...");
        
        try {
            const result = await generateNextQuestionAction(session.id);
            
            if (result.error) {
                toast.error(result.error);
                return;
            }
            
            if (result.data) {
                const { question, question_number, total_questions, is_last_question, message } = result.data;
                
                // Add the new question to session
                setSession(prev => ({
                    ...prev,
                    questions: [...prev.questions, question],
                }));
                
                setGeneratedQuestionCount(question_number);
                
                toast.success(message || `Question ${question_number}/${total_questions} generated`);
                
                if (is_last_question) {
                    toast.info("All questions have been generated!");
                }
            }
        } catch (error: any) {
            console.error("Error generating question:", error);
            toast.error("Failed to generate question. Please try again.");
        } finally {
            setIsGeneratingQuestion(false);
        }
    };

    const handleStart = async () => {
        setHasStarted(true);
        
        // If no questions exist yet, generate the first one
        if (session.questions.length === 0) {
            await generateNextQuestion();
        }
    };

    const currentQuestion = session.questions[currentQuestionIndex];

    // Show loading state while generating first question
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
                                <span className="text-2xl font-bold">{session.num_questions || 10}</span>
                            </div>
                            <div className="flex flex-col space-y-2 p-4 bg-muted/50 rounded-lg">
                                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                    Level
                                </span>
                                <span className="text-2xl font-bold capitalize">{difficulty}</span>
                            </div>
                        </div>

                        {topics.length > 0 && (
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
                        )}

                        {session.focus_areas && session.focus_areas.length > 0 && (
                            <div className="space-y-2">
                                <span className="text-sm font-medium">Focus Areas</span>
                                <div className="flex flex-wrap gap-2">
                                    {session.focus_areas.map((area, idx) => (
                                        <Badge key={idx} variant="secondary" className="capitalize">
                                            {area}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="space-y-2">
                            <span className="text-sm font-medium">Session Outline</span>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li className="flex items-center gap-2">
                                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    Introduction & Setup (Completed)
                                </li>
                                <li className="flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    Questions will be generated on-demand
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
    // Show loading state if no question is available yet
    if (!currentQuestion && isGeneratingQuestion) {
        return (
            <div className="w-full max-w-4xl mx-auto space-y-6">
                <Card className="min-h-[200px] flex flex-col items-center justify-center p-6">
                    <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                    <p className="text-lg font-medium text-center">Generating your first question...</p>
                    <p className="text-sm text-muted-foreground text-center mt-2">This may take 15-30 seconds</p>
                </Card>
            </div>
        );
    }

    // If no question and not generating, something went wrong
    if (!currentQuestion) {
        return (
            <div className="w-full max-w-4xl mx-auto space-y-6">
                <Card className="min-h-[200px] flex flex-col items-center justify-center p-6">
                    <p className="text-lg font-medium text-center text-destructive mb-4">No question available</p>
                    <Button onClick={() => generateNextQuestion()}>
                        Generate Question
                    </Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Question {currentQuestionIndex + 1} of {session.num_questions || 10}</h2>
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
                <Button 
                    variant="outline" 
                    className="mt-4" 
                    disabled={isGeneratingQuestion}
                    onClick={async () => {
                        // Move to next question
                        if (currentQuestionIndex < session.questions.length - 1) {
                            setCurrentQuestionIndex(prev => prev + 1);
                        } else {
                            // Need to generate next question
                            if (generatedQuestionCount < (session.num_questions || 10)) {
                                await generateNextQuestion();
                                // Auto-advance to the newly generated question
                                if (session.questions.length > currentQuestionIndex + 1) {
                                    setCurrentQuestionIndex(prev => prev + 1);
                                }
                            } else {
                                toast.success("Interview Finished!");
                                // TODO: Navigate to evaluation page
                            }
                        }
                    }}
                >
                    {isGeneratingQuestion ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Generating Question...
                        </>
                    ) : currentQuestionIndex < session.questions.length - 1 ? (
                        "Next Question (Demo)"
                    ) : generatedQuestionCount < (session.num_questions || 10) ? (
                        "Generate Next Question"
                    ) : (
                        "Finish Interview"
                    )}
                </Button>
            </div>
        </div>
    );
}
