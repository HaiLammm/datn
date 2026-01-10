"use server";

import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { interviewService } from "@/services/interview.service";
import { cvService } from "@/services/cv.service";
import {
    InterviewSessionCreate,
    InterviewCreateResponse,
    InterviewSessionListResponse,
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

        const result = await interviewService.createInterview(data, accessToken);

        revalidatePath("/interviews");
        return { message: "Interview created successfully", data: result };

    } catch (error: any) {
        console.error("Create interview error:", error);
        return {
            message: error.response?.data?.detail || "Failed to create interview session",
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
