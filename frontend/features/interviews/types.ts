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
    cv_id: z.string().uuid("Please select a valid CV"),
    job_description: z.string().min(10, "Job description must be at least 10 characters"),
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

export interface InterviewStatusResponse {
    session_id: string;
    status: string; // 'pending' | 'generating' | 'ready' | 'in_progress' | 'completed' | 'error'
    error_message?: string;
    questions?: InterviewQuestion[];
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

// ============ Evaluation Types (Story 8.3) ============

export interface DimensionScoreDetail {
    score: number;
    weight: number;
    sub_scores: Record<string, number>;
    evidence: string[];
    analysis?: string;
}

export interface InterviewEvaluationResponse {
    id: string;
    interview_session_id: string;
    final_score: number;
    grade: string;
    hiring_recommendation: string;
    dimension_scores: {
        technical_competency?: DimensionScoreDetail;
        technical_competence?: DimensionScoreDetail;
        communication_skills: DimensionScoreDetail;
        behavioral_fit: DimensionScoreDetail;
    };
    detailed_analysis: {
        key_strengths?: string[];
        strengths?: string[];
        areas_for_improvement?: string[];
        weaknesses?: string[];
        notable_moments: string[];
        red_flags?: string[];
    };
    recommendations: {
        hiring_decision: string;
        reasoning: string;
        role_fit?: string;
        suggested_role_fit?: string;
        onboarding_suggestions?: string[];
        development_areas?: string[];
        development_suggestions?: string[];
    };
    evaluation_metadata?: {
        total_questions?: number;
        questions_by_category?: Record<string, number>;
        interview_duration?: number;
        model_used?: string;
    };
    created_at: string;
    updated_at: string;
}

// ============ Story 8.4: Interview History Types ============

export interface InterviewSessionSummary {
    id: string;
    job_title: string;
    created_at: string;
    completed_at?: string | null;
    status: string;
    overall_score?: number | null;
    overall_grade?: string | null;
    duration_minutes?: number | null;
    question_count: number;
    turn_count: number;
}

export interface InterviewSessionDetail extends InterviewSessionSummary {
    job_description?: string | null;
    position_level?: string | null;
    hiring_recommendation?: string | null;
    total_turns?: number | null;
}

export interface PaginatedInterviewSessions {
    items: InterviewSessionSummary[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface TranscriptTurn {
    turn_number: number;
    question_text?: string | null;
    question_type?: string | null;
    candidate_message: string;
    ai_response: string;
    scores?: {
        technical_score?: number;
        communication_score?: number;
        depth_score?: number;
        overall_score?: number;
    } | null;
    action_type?: string | null;
    created_at: string;
}

export interface InterviewTranscriptResponse {
    interview_id: string;
    job_title: string;
    total_turns: number;
    turns: TranscriptTurn[];
}

export interface OverallEvaluation {
    score: number;
    grade: string;
    hiring_recommendation: string;
}

export interface DimensionDetail {
    score: number;
    weight: number;
    sub_scores: Record<string, number>;
    evidence: string[];
}

export interface DimensionScoresDetail {
    technical: DimensionDetail;
    communication: DimensionDetail;
    behavioral: DimensionDetail;
}

export interface DetailedAnalysisSection {
    key_strengths: string[];
    areas_for_improvement: string[];
    notable_moments: string[];
    red_flags?: string[];
}

export interface RecommendationsSection {
    hiring_decision: string;
    reasoning: string;
    role_fit: string;
    onboarding_suggestions?: string[];
    development_areas: string[];
}

export interface InterviewEvaluationDetail {
    interview_id: string;
    job_title: string;
    overall_evaluation: OverallEvaluation;
    dimension_scores: DimensionScoresDetail;
    detailed_analysis: DetailedAnalysisSection;
    recommendations: RecommendationsSection;
    created_at: string;
}
