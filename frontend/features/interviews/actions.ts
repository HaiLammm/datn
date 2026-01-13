"use server";

import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { interviewService } from "@/services/interview.service";
import { cvService } from "@/services/cv.service";
import {
    InterviewSessionCreate,
    InterviewCreateResponse,
    InterviewSessionListResponse,
    InterviewStatusResponse,
    PaginatedInterviewSessions,
    InterviewSessionDetail,
    InterviewTranscriptResponse,
    InterviewEvaluationDetail,
} from "./types";
import { CVWithStatus } from "@datn/shared-types";

async function getAccessToken(): Promise<string> {
    const headersList = await headers();
    const cookieHeader = headersList.get("cookie") || "";
    const cookies = cookieHeader.split(";").map((c) => c.trim());
    const accessTokenCookie = cookies.find((c) => c.startsWith("access_token="));
    return accessTokenCookie ? accessTokenCookie.split("=")[1] : "";
}

export async function createInterviewAction(
    prevState: any,
    formData: FormData
): Promise<{ message: string; errors?: Record<string, string>; data?: InterviewCreateResponse }> {
    try {
        const accessToken = await getAccessToken();

        const jobDescription = formData.get("job_description") as string;
        const cvContent = formData.get("cv_content") as string;
        const positionLevel = formData.get("position_level") as "junior" | "middle" | "senior";
        const numQuestions = parseInt(formData.get("num_questions") as string) || 10;
        const focusAreasStr = formData.get("focus_areas") as string;
        const focusAreas = focusAreasStr ? focusAreasStr.split(",").map((s) => s.trim()) : undefined;

        // Basic validation
        const errors: Record<string, string> = {};
        if (!jobDescription || jobDescription.length < 10) {
            errors.job_description = "Job description must be at least 10 characters";
        }
        if (!cvContent || cvContent.length < 10) {
            errors.cv_content = "CV content must be at least 10 characters";
        }
        if (!positionLevel) {
            errors.position_level = "Position level is required";
        }

        if (Object.keys(errors).length > 0) {
            return { message: "Validation failed", errors };
        }

        // Call service
        const data: InterviewSessionCreate = {
            job_description: jobDescription,
            cv_content: cvContent,
            position_level: positionLevel,
            num_questions: numQuestions,
            focus_areas: focusAreas,
        };

        // Create interview (returns immediately)
        const result = await interviewService.createInterview(data, accessToken);
        
        // Poll for status until ready
        const finalResult = await pollInterviewStatus(result.session.id, accessToken);

        revalidatePath("/interviews");
        return { message: "Interview created successfully", data: finalResult };

    } catch (error: any) {
        console.error("Create interview error:", error);
        return {
            message: error.response?.data?.detail || "Failed to create interview session",
        };
    }
}

/**
 * Poll interview status until questions are ready or timeout
 */
async function pollInterviewStatus(
    sessionId: string, 
    accessToken: string,
    maxAttempts: number = 60,  // 60 attempts
    intervalMs: number = 3000   // 3 seconds interval
): Promise<InterviewCreateResponse> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        // Wait before checking status (except first attempt)
        if (attempt > 1) {
            await new Promise(resolve => setTimeout(resolve, intervalMs));
        }
        
        try {
            const status = await interviewService.getInterviewStatus(sessionId, accessToken);
            
            console.log(`[Poll ${attempt}/${maxAttempts}] Status: ${status.status}`);
            
            // Success - questions ready
            if (status.status === 'ready') {
                return {
                    session: { 
                        id: status.session_id,
                        status: status.status,
                        // ... other session fields will be populated by service
                    } as any,
                    questions: status.questions || [],
                    message: status.message
                };
            }
            
            // Error occurred
            if (status.status === 'error') {
                throw new Error(status.error_message || 'Question generation failed');
            }
            
            // Continue polling for: 'pending', 'generating'
            
        } catch (error: any) {
            console.error(`[Poll ${attempt}] Error:`, error);
            
            // Don't retry if it's a 404 or 403
            if (error.response?.status === 404 || error.response?.status === 403) {
                throw error;
            }
            
            // Retry on network errors
        }
    }
    
    // Timeout
    throw new Error(`Question generation timed out after ${maxAttempts * intervalMs / 1000} seconds. Please try again later.`);
}

export async function getInterviewStatusAction(
    interviewId: string
): Promise<{ data?: InterviewStatusResponse; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const status = await interviewService.getInterviewStatus(interviewId, accessToken);
        return { data: status };
    } catch (error: any) {
        console.error("Error fetching interview status:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch interview status",
        };
    }
}

export async function getCVListAction(): Promise<CVWithStatus[]> {
    try {
        const accessToken = await getAccessToken();
        return await cvService.getCVList(accessToken);
    } catch (error) {
        console.error("Error fetching CV list:", error);
        return [];
    }
}

export async function getEvaluationAction(
    interviewId: string
): Promise<{ data?: any; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const evaluation = await interviewService.getEvaluation(interviewId, accessToken);
        return { data: evaluation };
    } catch (error: any) {
        console.error("Error fetching evaluation:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch evaluation report",
        };
    }
}

export async function completeInterviewAction(
    interviewId: string,
    forceComplete: boolean = false
): Promise<{ data?: any; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const result = await interviewService.completeInterview(interviewId, forceComplete, accessToken);
        revalidatePath(`/interviews/${interviewId}`);
        revalidatePath(`/interviews/${interviewId}/evaluation`);
        return { data: result };
    } catch (error: any) {
        console.error("Error completing interview:", error);
        return {
            error: error.response?.data?.detail || "Failed to complete interview",
        };
    }
}

export async function getTranscriptAction(
    interviewId: string
): Promise<{ data?: any; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const transcript = await interviewService.getTranscript(interviewId, accessToken);
        return { data: transcript };
    } catch (error: any) {
        console.error("Error fetching transcript:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch transcript",
        };
    }
}

export async function listInterviewsAction(
    limit: number = 20,
    skip: number = 0
): Promise<{ data?: InterviewSessionListResponse; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const interviews = await interviewService.listInterviews(limit, skip, accessToken);
        return { data: interviews };
    } catch (error: any) {
        console.error("Error fetching interviews:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch interviews",
        };
    }
}

// ============ Story 8.4: Interview History Actions ============

/**
 * Get paginated interview history with sorting and filtering
 */
export async function getInterviewHistoryAction(params?: {
    page?: number;
    page_size?: number;
    sort_by?: "created_at" | "overall_score";
    sort_order?: "asc" | "desc";
    status?: string;
}): Promise<{ data?: PaginatedInterviewSessions; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const history = await interviewService.getInterviewHistory(params || {}, accessToken);
        return { data: history };
    } catch (error: any) {
        console.error("Error fetching interview history:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch interview history",
        };
    }
}

/**
 * Get detailed information about a single interview session
 */
export async function getInterviewDetailAction(
    sessionId: string
): Promise<{ data?: InterviewSessionDetail; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const detail = await interviewService.getInterviewDetail(sessionId, accessToken);
        return { data: detail };
    } catch (error: any) {
        console.error("Error fetching interview detail:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch interview detail",
        };
    }
}

/**
 * Get full conversation transcript for an interview session
 */
export async function getInterviewTranscriptAction(
    sessionId: string
): Promise<{ data?: InterviewTranscriptResponse; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const transcript = await interviewService.getInterviewTranscript(sessionId, accessToken);
        return { data: transcript };
    } catch (error: any) {
        console.error("Error fetching interview transcript:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch interview transcript",
        };
    }
}

/**
 * Get comprehensive evaluation report for an interview session
 */
export async function getEvaluationDetailAction(
    sessionId: string
): Promise<{ data?: InterviewEvaluationDetail; error?: string }> {
    try {
        const accessToken = await getAccessToken();
        const evaluation = await interviewService.getEvaluationDetail(sessionId, accessToken);
        return { data: evaluation };
    } catch (error: any) {
        console.error("Error fetching evaluation detail:", error);
        return {
            error: error.response?.data?.detail || "Failed to fetch evaluation detail",
        };
    }
}
