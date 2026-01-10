import { z } from "zod";

export const InterviewSessionSchema = z.object({
    id: z.string(),
    candidate_id: z.number(),
    job_posting_id: z.string().nullable().optional(),
    status: z.string(),
    scheduled_at: z.string().nullable().optional(),
    started_at: z.string().nullable().optional(),
    completed_at: z.string().nullable().optional(),
    duration_minutes: z.number().nullable().optional(),
    created_at: z.string(),
    updated_at: z.string(),
});

export type InterviewSession = z.infer<typeof InterviewSessionSchema>;

export const InterviewQuestionSchema = z.object({
    id: z.string(),
    interview_session_id: z.string(),
    question_id: z.string(),
    category: z.string(),
    difficulty: z.string(),
    question_text: z.string(),
    key_points: z.array(z.string()).nullable().optional(),
    ideal_answer_outline: z.string().nullable().optional(),
    evaluation_criteria: z.array(z.string()).nullable().optional(),
    order_index: z.number(),
    is_selected: z.boolean(),
    created_at: z.string(),
});

export type InterviewQuestion = z.infer<typeof InterviewQuestionSchema>;

export const InterviewSessionCreateSchema = z.object({
    job_description: z.string().min(10, "Job description must be at least 10 characters"),
    cv_content: z.string().min(10, "CV content must be at least 10 characters"),
    position_level: z.enum(["junior", "middle", "senior"]),
    num_questions: z.number().min(5).max(15).optional().default(10),
    focus_areas: z.array(z.string()).optional(),
});

export type InterviewSessionCreate = z.infer<typeof InterviewSessionCreateSchema>;

export interface InterviewCreateResponse {
    session: InterviewSession;
    questions: InterviewQuestion[];
    message: string;
}

// ============ Interview Turn Types (Story 8.2) ============

export const TurnEvaluationSchema = z.object({
    technical_score: z.number().min(0).max(10),
    communication_score: z.number().min(0).max(10),
    depth_score: z.number().min(0).max(10),
    overall_score: z.number().min(0).max(10),
});

export type TurnEvaluation = z.infer<typeof TurnEvaluationSchema>;

export const NextActionSchema = z.object({
    action_type: z.enum(['follow_up', 'continue', 'next_question', 'end']),
    ai_response: z.string(),
    follow_up_question: z.string().optional(),
});

export type NextAction = z.infer<typeof NextActionSchema>;

export const ContextUpdateSchema = z.object({
    topics_covered: z.array(z.string()).default([]),
    follow_up_depth: z.number().min(0).default(0),
    turn_count: z.number().min(1),
});

export type ContextUpdate = z.infer<typeof ContextUpdateSchema>;

export const ProcessTurnResponseSchema = z.object({
    turn_evaluation: TurnEvaluationSchema,
    next_action: NextActionSchema,
    context_update: ContextUpdateSchema,
    turn_id: z.string(),
});

export type ProcessTurnResponse = z.infer<typeof ProcessTurnResponseSchema>;

export interface ProcessTurnRequest {
    current_question_id: string;
    candidate_message: string;
}

// Legacy types (kept for backwards compatibility)
export interface InterviewTurnResponse {
    id: string;
    interview_session_id: string;
    question_id?: string;
    turn_number: number;
    ai_message: string;
    candidate_message: string;
    answer_quality?: {
        technical_accuracy: number;
        communication_clarity: number;
        depth_of_knowledge: number;
        overall_score: number;
    };
    key_observations?: string[];
    strengths?: string[];
    gaps?: string[];
    action_type?: string;
    created_at: string;
}

export interface InterviewTurnListResponse {
    turns: InterviewTurnResponse[];
    total: number;
}

export interface InterviewSessionComplete extends InterviewSession {
    questions: InterviewQuestion[];
    turns: InterviewTurnResponse[];
    evaluation?: InterviewEvaluationResponse;
}

export interface InterviewSessionListResponse {
    sessions: InterviewSession[];
    total: number;
}

export interface InterviewCompleteResponse {
    session: InterviewSession;
    evaluation: InterviewEvaluationResponse;
    message: string;
}

export interface InterviewEvaluationResponse {
    id: string;
    interview_session_id: string;
    final_score: number;
    grade: string;
    hiring_recommendation: string;
    dimension_scores: {
        technical_competence: Record<string, number>;
        communication_skills: Record<string, number>;
        behavioral_fit: Record<string, number>;
    };
    detailed_analysis: {
        strengths: string[];
        weaknesses: string[];
        notable_moments: string[];
        red_flags?: string[];
    };
    recommendations: {
        hiring_decision: string;
        reasoning: string;
        development_suggestions?: string[];
    };
    evaluation_metadata?: Record<string, any>;
    created_at: string;
    updated_at: string;
}
