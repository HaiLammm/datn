"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, MessageSquare, User } from "lucide-react";
import type { InterviewTurnResponse, InterviewQuestion } from "../types";

interface TranscriptReviewProps {
    turns: InterviewTurnResponse[];
    questions: InterviewQuestion[];
}

export function TranscriptReview({ turns, questions }: TranscriptReviewProps) {
    const [expandedTurns, setExpandedTurns] = useState<Record<number, boolean>>({});

    const toggleTurn = (turnNumber: number) => {
        setExpandedTurns(prev => ({ ...prev, [turnNumber]: !prev[turnNumber] }));
    };

    const getScoreColor = (score: number) => {
        if (score >= 8) return "bg-green-500";
        if (score >= 6) return "bg-blue-500";
        if (score >= 4) return "bg-yellow-500";
        return "bg-red-500";
    };

    const getScoreTextColor = (score: number) => {
        if (score >= 8) return "text-green-600";
        if (score >= 6) return "text-blue-600";
        if (score >= 4) return "text-yellow-600";
        return "text-red-600";
    };

    // Map questions by ID for quick lookup
    const questionsMap = questions.reduce((acc, q) => {
        acc[q.id] = q;
        return acc;
    }, {} as Record<string, InterviewQuestion>);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Interview Transcript</h2>
                <Badge variant="outline">{turns.length} Turns</Badge>
            </div>

            <div className="space-y-3">
                {turns.map((turn) => {
                    const question = turn.question_id ? questionsMap[turn.question_id] : null;
                    const isExpanded = expandedTurns[turn.turn_number];

                    return (
                        <Collapsible
                            key={turn.id}
                            open={isExpanded}
                            onOpenChange={() => toggleTurn(turn.turn_number)}
                        >
                            <Card className={turn.answer_quality ? "border-l-4" : ""} style={{
                                borderLeftColor: turn.answer_quality 
                                    ? (turn.answer_quality.overall_score >= 7 ? "rgb(34, 197, 94)" : 
                                       turn.answer_quality.overall_score >= 5 ? "rgb(59, 130, 246)" : 
                                       "rgb(234, 179, 8)")
                                    : undefined
                            }}>
                                <CollapsibleTrigger className="w-full">
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0">
                                        <div className="flex items-center gap-3">
                                            <Badge variant="outline">Turn {turn.turn_number}</Badge>
                                            {question && (
                                                <Badge variant="secondary">
                                                    {question.category}
                                                </Badge>
                                            )}
                                            {turn.answer_quality && (
                                                <span className={`font-semibold ${getScoreTextColor(turn.answer_quality.overall_score)}`}>
                                                    Score: {turn.answer_quality.overall_score.toFixed(1)}/10
                                                </span>
                                            )}
                                        </div>
                                        {isExpanded ? 
                                            <ChevronUp className="h-4 w-4" /> : 
                                            <ChevronDown className="h-4 w-4" />
                                        }
                                    </CardHeader>
                                </CollapsibleTrigger>

                                <CollapsibleContent>
                                    <CardContent className="space-y-4">
                                        {/* Question Section */}
                                        {question && (
                                            <div className="bg-muted/50 p-4 rounded-lg">
                                                <div className="flex items-start gap-2 mb-2">
                                                    <MessageSquare className="h-5 w-5 text-blue-500 mt-0.5" />
                                                    <div className="flex-1">
                                                        <p className="font-semibold mb-1">Question:</p>
                                                        <p className="text-sm">{question.question_text}</p>
                                                    </div>
                                                </div>
                                                {question.evaluation_criteria && question.evaluation_criteria.length > 0 && (
                                                    <div className="mt-3 pl-7">
                                                        <p className="text-xs text-muted-foreground font-semibold mb-1">
                                                            Evaluation Criteria:
                                                        </p>
                                                        <ul className="text-xs text-muted-foreground space-y-0.5">
                                                            {question.evaluation_criteria.map((criterion, idx) => (
                                                                <li key={idx}>• {criterion}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* AI Message */}
                                        <div className="flex items-start gap-2">
                                            <MessageSquare className="h-5 w-5 text-blue-500 mt-0.5" />
                                            <div className="flex-1">
                                                <p className="font-semibold text-sm mb-1">AI Interviewer:</p>
                                                <p className="text-sm text-muted-foreground">{turn.ai_message}</p>
                                            </div>
                                        </div>

                                        {/* Candidate Answer */}
                                        <div className="flex items-start gap-2">
                                            <User className="h-5 w-5 text-green-500 mt-0.5" />
                                            <div className="flex-1">
                                                <p className="font-semibold text-sm mb-1">Your Answer:</p>
                                                <p className="text-sm">{turn.candidate_message}</p>
                                            </div>
                                        </div>

                                        {/* Per-Turn Evaluation */}
                                        {turn.answer_quality && (
                                            <div className="bg-muted/50 p-4 rounded-lg space-y-3">
                                                <p className="font-semibold text-sm">Turn Evaluation:</p>
                                                
                                                {/* Score Breakdown */}
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Technical</p>
                                                        <p className={`font-semibold ${getScoreTextColor(turn.answer_quality.technical_accuracy)}`}>
                                                            {turn.answer_quality.technical_accuracy.toFixed(1)}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Communication</p>
                                                        <p className={`font-semibold ${getScoreTextColor(turn.answer_quality.communication_clarity)}`}>
                                                            {turn.answer_quality.communication_clarity.toFixed(1)}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Depth</p>
                                                        <p className={`font-semibold ${getScoreTextColor(turn.answer_quality.depth_of_knowledge)}`}>
                                                            {turn.answer_quality.depth_of_knowledge.toFixed(1)}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Overall</p>
                                                        <p className={`font-semibold ${getScoreTextColor(turn.answer_quality.overall_score)}`}>
                                                            {turn.answer_quality.overall_score.toFixed(1)}
                                                        </p>
                                                    </div>
                                                </div>

                                                {/* Strengths */}
                                                {turn.strengths && turn.strengths.length > 0 && (
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1 text-green-600">Strengths:</p>
                                                        <ul className="text-xs text-muted-foreground space-y-0.5">
                                                            {turn.strengths.map((strength, idx) => (
                                                                <li key={idx}>✓ {strength}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {/* Gaps */}
                                                {turn.gaps && turn.gaps.length > 0 && (
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1 text-yellow-600">Areas to Improve:</p>
                                                        <ul className="text-xs text-muted-foreground space-y-0.5">
                                                            {turn.gaps.map((gap, idx) => (
                                                                <li key={idx}>⚠ {gap}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {/* Key Observations */}
                                                {turn.key_observations && turn.key_observations.length > 0 && (
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1">Observations:</p>
                                                        <ul className="text-xs text-muted-foreground space-y-0.5">
                                                            {turn.key_observations.map((obs, idx) => (
                                                                <li key={idx}>• {obs}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {/* Action Type */}
                                                {turn.action_type && (
                                                    <div className="pt-2 border-t">
                                                        <p className="text-xs text-muted-foreground">
                                                            Next Action: <span className="font-semibold">{turn.action_type.replace(/_/g, " ")}</span>
                                                        </p>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </CardContent>
                                </CollapsibleContent>
                            </Card>
                        </Collapsible>
                    );
                })}
            </div>

            {turns.length === 0 && (
                <Card>
                    <CardContent className="py-10 text-center text-muted-foreground">
                        No conversation turns yet. Start the interview to see the transcript.
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
