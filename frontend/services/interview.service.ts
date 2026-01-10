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
            const response = await apiClient.get<InterviewSessionListResponse>(
                "/interviews",
                {
                    params: { limit, skip },
                    headers,
                }
            );
            return response.data;
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
};
