"use server";

import { z } from "zod";
import { cvService } from "@/services/cv.service";
import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { CVWithStatus, CVAnalysis, AnalysisStatus, SkillSuggestionsResponse } from "@datn/shared-types";

interface ActionState {
  message: string;
  errors: Record<string, string>;
}

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

const CVSchema = z.object({
  cvFile: z
    .instanceof(File)
    .refine((file) => file.size > 0, "File không được để trống.")
    .refine((file) => file.size <= MAX_FILE_SIZE, `Kích thước file tối đa là 5MB.`)
    .refine(
      (file) => ACCEPTED_FILE_TYPES.includes(file.type),
      "Chỉ chấp nhận file PDF hoặc DOCX."
    ),
});

async function getAccessToken(): Promise<string> {
  const headersList = await headers();
  const cookieHeader = headersList.get('cookie') || '';
  const cookies = cookieHeader.split(';').map(c => c.trim());
  const accessTokenCookie = cookies.find(c => c.startsWith('access_token='));
  return accessTokenCookie ? accessTokenCookie.split('=')[1] : '';
}

export async function createCVAction(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  try {
    // Validate form data
    const validatedFields = CVSchema.safeParse({
      cvFile: formData.get("cvFile"),
    });

    if (!validatedFields.success) {
      const fieldErrors = validatedFields.error.flatten().fieldErrors;
      return {
        message: "Lỗi validation.",
        errors: {
          cvFile: fieldErrors.cvFile ? fieldErrors.cvFile[0] : "",
        },
      };
    }

    const { cvFile } = validatedFields.data;

    // Create a new FormData object for the service call
    const serviceFormData = new FormData();
    serviceFormData.append("file", cvFile);

    // Get authentication token from cookies to forward to backend API
    const accessToken = await getAccessToken();

    // Upload CV with forwarded authentication token
    await cvService.uploadCV(serviceFormData, accessToken);

    revalidatePath("/cvs/upload"); // Revalidate the upload page
    revalidatePath("/cvs"); // Revalidate the CV list page
    revalidatePath("/dashboard"); // Revalidate the dashboard page

    return { message: "CV đã được tải lên thành công!", errors: {} };
  } catch (error: unknown) {
    console.error("Server Action Error:", error);
    let errorMessage = "Đã xảy ra lỗi khi tải lên CV.";
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      errorMessage = axiosError.response?.data?.detail || errorMessage;
    }
    return {
      message: errorMessage,
      errors: {},
    };
  }
}

export async function getCVList(): Promise<CVWithStatus[]> {
  try {
    const accessToken = await getAccessToken();
    return await cvService.getCVList(accessToken);
  } catch (error) {
    console.error("Error fetching CV list:", error);
    return [];
  }
}

export async function getCVAnalysis(cvId: string): Promise<CVAnalysis> {
  const accessToken = await getAccessToken();
  return await cvService.getAnalysis(cvId, accessToken);
}

export async function getCVAnalysisStatus(cvId: string): Promise<AnalysisStatus> {
  const accessToken = await getAccessToken();
  return await cvService.getAnalysisStatus(cvId, accessToken);
}

export async function deleteCVAction(cvId: string): Promise<{ success: boolean; message: string }> {
  try {
    const accessToken = await getAccessToken();
    await cvService.deleteCV(cvId, accessToken);
    revalidatePath("/cvs");
    revalidatePath("/dashboard");
    return { success: true, message: "CV deleted successfully." };
  } catch (error) {
    console.error("Server Action Delete Error:", error);
    let errorMessage = "Đã xảy ra lỗi khi xóa CV.";
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      errorMessage = axiosError.response?.data?.detail || errorMessage;
    }
    return { success: false, message: errorMessage };
  }
}

export async function updateCVVisibilityAction(
  cvId: string, 
  isPublic: boolean
): Promise<{ success: boolean; error?: string }> {
  try {
    const accessToken = await getAccessToken();
    
    if (!accessToken) {
      console.error("updateCVVisibilityAction: No access token found in cookies");
      return { success: false, error: "Authentication required. Please log in again." };
    }
    
    await cvService.updateVisibility(cvId, isPublic, accessToken);
    revalidatePath("/cvs");
    return { success: true };
  } catch (error) {
    console.error("updateCVVisibilityAction: Error caught:", error);
    
    let errorMessage = "Failed to update CV visibility.";
    
    if (error && typeof error === "object") {
      if ("response" in error) {
        const axiosError = error as { 
          response?: { 
            status?: number;
            data?: { detail?: string } 
          } 
        };
        
        const status = axiosError.response?.status;
        const detail = axiosError.response?.data?.detail;
        
        if (status === 401) {
          errorMessage = "Session expired. Please log in again.";
        } else if (status === 403) {
          errorMessage = "You don't have permission to modify this CV.";
        } else if (status === 404) {
          errorMessage = "CV not found.";
        } else if (detail) {
          errorMessage = detail;
        }
      } else if ("message" in error) {
        errorMessage = (error as Error).message;
      }
    }
    
    return { success: false, error: errorMessage };
  }
}

/**
 * Get the download URL for a CV file.
 * This action returns the URL that can be used to download the CV.
 * The actual download is handled client-side in the DownloadCVButton component.
 */
export async function getDownloadCVUrl(cvId: string): Promise<string> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  return `${apiUrl}/cvs/${cvId}/download`;
}

/**
 * Server Action to fetch skill suggestions for a given CV.
 */
export async function getSkillSuggestions(cvId: string): Promise<SkillSuggestionsResponse> {
  try {
    const accessToken = await getAccessToken();
    return await cvService.getSkillSuggestions(cvId, accessToken);
  } catch (error) {
    console.error("Error fetching skill suggestions:", error);
    // Return an empty suggestions object in case of error
    return { suggestions: [] };
  }
}

