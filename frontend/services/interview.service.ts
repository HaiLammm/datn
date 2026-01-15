import { apiClient } from "@/services/api-client";
import {
    InterviewCreateResponse,
    InterviewSessionCreate,
    InterviewSessionListResponse,
    InterviewSessionComplete,
    InterviewQuestion,
    InterviewTurnResponse,
    InterviewTurnListResponse,
    InterviewCompleteResponse,
    InterviewEvaluationResponse,
    ProcessTurnRequest,
    ProcessTurnResponse,
    InterviewStatusResponse,
    // Story 8.4: Interview History types
    PaginatedInterviewSessions,
    InterviewSessionDetail,
    InterviewTranscriptResponse,
    InterviewEvaluationDetail,
} from "@/features/interviews/types";

export const interviewService = {
    createInterview: async (
        data: InterviewSessionCreate,
        accessToken?: string
    ): Promise<InterviewCreateResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.post<InterviewCreateResponse>(
                "/interviews",
                data,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error creating interview:", error);
            throw error;
        }
    },

    listInterviews: async (
        limit: number = 20,
        skip: number = 0,
        accessToken?: string
    ): Promise<InterviewSessionListResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            
            // Convert limit/skip to page/page_size for new backend API
            const page_size = limit;
            const page = Math.floor(skip / limit) + 1; // Convert skip to 1-indexed page
            
            const response = await apiClient.get<PaginatedInterviewSessions>(
                "/interviews",
                {
                    params: { page, page_size },
                    headers,
                }
            );
            
            // Map PaginatedInterviewSessions to InterviewSessionListResponse
            return {
                sessions: response.data.items as any[], // InterviewSessionSummary → InterviewSession
                total: response.data.total,
            };
        } catch (error) {
            console.error("Error listing interviews:", error);
            throw error;
        }
    },

    getInterview: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewSessionComplete> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewSessionComplete>(
                `/interviews/${sessionId}`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting interview:", error);
            throw error;
        }
    },

    /**
     * Get interview question generation status (polling endpoint).
     * Used for async question generation flow.
     */
    getInterviewStatus: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewStatusResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewStatusResponse>(
                `/interviews/${sessionId}/status`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting interview status:", error);
            throw error;
        }
    },

    getQuestions: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewQuestion[]> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewQuestion[]>(
                `/interviews/${sessionId}/questions`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting questions:", error);
            throw error;
        }
    },

    /**
     * Process a conversation turn with DialogFlow AI.
     * Story 8.2: Voice Interaction with AI Interviewer
     * 
     * @param sessionId - Interview session UUID
     * @param data - Turn request data (current_question_id, candidate_message)
     * @param accessToken - Optional authentication token
     * @returns ProcessTurnResponse with evaluation, next_action, context_update, turn_id
     * 
     * @throws {Error} 403 - User doesn't own the session
     * @throws {Error} 400 - Invalid session state or bad input
     * @throws {Error} 503 - Ollama/AI service unavailable
     * @throws {Error} 500 - Unexpected server error
     */
    processTurn: async (
        sessionId: string,
        data: ProcessTurnRequest,
        accessToken?: string
    ): Promise<ProcessTurnResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.post<ProcessTurnResponse>(
                `/interviews/${sessionId}/turns`,
                data,
                { headers }
            );
            return response.data;
        } catch (error: any) {
            console.error("Error processing turn:", error);
            
            // Enhanced error handling with user-friendly messages
            if (error.response) {
                const status = error.response.status;
                const detail = error.response.data?.detail || error.message;
                
                switch (status) {
                    case 403:
                        throw new Error(`Access denied: ${detail}`);
                    case 400:
                        throw new Error(`Invalid request: ${detail}`);
                    case 503:
                        throw new Error(
                            "AI service is temporarily unavailable. Please try again in a moment."
                        );
                    case 500:
                        throw new Error(
                            "Server error occurred while processing your answer. Please try again."
                        );
                    default:
                        throw new Error(`Error: ${detail}`);
                }
            }
            
            // Network errors
            if (error.code === 'ERR_NETWORK') {
                throw new Error(
                    "Network error. Please check your internet connection and try again."
                );
            }
            
            throw error;
        }
    },

    completeInterview: async (
        sessionId: string,
        forceComplete: boolean = false,
        accessToken?: string
    ): Promise<InterviewCompleteResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.post<InterviewCompleteResponse>(
                `/interviews/${sessionId}/complete`,
                { force_complete: forceComplete },
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error completing interview:", error);
            throw error;
        }
    },

    /**
     * Get evaluation report for a completed interview.
     * Story 8.3: Interview Performance Report
     */
    getEvaluation: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewEvaluationResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewEvaluationResponse>(
                `/interviews/${sessionId}/evaluation`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting evaluation:", error);
            throw error;
        }
    },

    /**
     * Get full conversation transcript for an interview.
     * Story 8.3: Interview Performance Report
     */
    getTranscript: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewTurnListResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewTurnListResponse>(
                `/interviews/${sessionId}/turns`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting transcript:", error);
            throw error;
        }
    },

    // ============ Story 8.4: Interview History Methods ============

    /**
     * Get paginated list of interview sessions with filtering and sorting.
     * Story 8.4: Interview History
     */
    getInterviewHistory: async (
        params: {
            page?: number;
            page_size?: number;
            sort_by?: "created_at" | "overall_score";
            sort_order?: "asc" | "desc";
            status?: string;
        } = {},
        accessToken?: string
    ): Promise<PaginatedInterviewSessions> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }

            const queryParams = new URLSearchParams();
            if (params.page) queryParams.append("page", params.page.toString());
            if (params.page_size) queryParams.append("page_size", params.page_size.toString());
            if (params.sort_by) queryParams.append("sort_by", params.sort_by);
            if (params.sort_order) queryParams.append("sort_order", params.sort_order);
            if (params.status) queryParams.append("status", params.status);

            const url = `/interviews${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;

            const response = await apiClient.get<PaginatedInterviewSessions>(url, { headers });
            return response.data;
        } catch (error) {
            console.error("Error getting interview history:", error);
            throw error;
        }
    },

    /**
     * Get detailed information about a specific interview session.
     * Story 8.4: Interview History
     */
    getInterviewDetail: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewSessionDetail> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewSessionDetail>(
                `/interviews/${sessionId}/detail`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting interview detail:", error);
            throw error;
        }
    },

    /**
     * Get full conversation transcript for an interview session.
     * Story 8.4: Interview History
     */
    getInterviewTranscript: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewTranscriptResponse> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewTranscriptResponse>(
                `/interviews/${sessionId}/transcript`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting interview transcript:", error);
            throw error;
        }
    },

    /**
     * Get comprehensive evaluation report for a completed interview.
     * Story 8.4: Interview History
     */
    getEvaluationDetail: async (
        sessionId: string,
        accessToken?: string
    ): Promise<InterviewEvaluationDetail> => {
        try {
            const headers: Record<string, string> = {};
            if (accessToken) {
                headers.Authorization = `Bearer ${accessToken}`;
            }
            const response = await apiClient.get<InterviewEvaluationDetail>(
                `/interviews/${sessionId}/evaluation/detail`,
                { headers }
            );
            return response.data;
        } catch (error) {
            console.error("Error getting evaluation detail:", error);
            throw error;
        }
    },
};
