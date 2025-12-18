"use server";

import { z } from "zod";
import { jobService } from "@/services/job.service";
import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import {
  JobDescriptionResponse,
  JDParseStatusResponse,
  ParsedJDRequirements,
  LocationType,
  RankedCandidateListResponse,
  CandidateQueryParams,
  RecruiterCVAccessResponse,
} from "@datn/shared-types";

export interface ActionState {
  message: string;
  errors: Record<string, string>;
  data?: JobDescriptionResponse;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

const JDTextSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  description: z.string().min(10, "Mô tả phải có ít nhất 10 ký tự"),
  location_type: z.enum(["remote", "hybrid", "on-site"]).default("remote"),
  required_skills: z.string().optional(),
  min_experience_years: z.string().optional(),
  salary_min: z.string().optional(),
  salary_max: z.string().optional(),
});

const JDFileSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  jdFile: z
    .instanceof(File)
    .refine((file) => file.size > 0, "File không được để trống.")
    .refine(
      (file) => file.size <= MAX_FILE_SIZE,
      "Kích thước file tối đa là 10MB."
    )
    .refine(
      (file) => ACCEPTED_FILE_TYPES.includes(file.type),
      "Chỉ chấp nhận file PDF hoặc DOCX."
    ),
  location_type: z.enum(["remote", "hybrid", "on-site"]).default("remote"),
  required_skills: z.string().optional(),
  min_experience_years: z.string().optional(),
  salary_min: z.string().optional(),
  salary_max: z.string().optional(),
});

async function getAccessToken(): Promise<string> {
  const headersList = await headers();
  const cookieHeader = headersList.get("cookie") || "";
  const cookies = cookieHeader.split(";").map((c) => c.trim());
  const accessTokenCookie = cookies.find((c) => c.startsWith("access_token="));
  return accessTokenCookie ? accessTokenCookie.split("=")[1] : "";
}

function parseSkillsString(skills: string | undefined): string[] | undefined {
  if (!skills || skills.trim() === "") return undefined;
  return skills
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function parseNumberString(value: string | undefined): number | undefined {
  if (!value || value.trim() === "") return undefined;
  const num = parseInt(value, 10);
  return isNaN(num) ? undefined : num;
}

export async function createJDAction(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  try {
    const inputMode = formData.get("inputMode") as string;
    const accessToken = await getAccessToken();

    if (inputMode === "file") {
      // File upload mode
      const validatedFields = JDFileSchema.safeParse({
        title: formData.get("title"),
        jdFile: formData.get("jdFile"),
        location_type: formData.get("location_type") || "remote",
        required_skills: formData.get("required_skills"),
        min_experience_years: formData.get("min_experience_years"),
        salary_min: formData.get("salary_min"),
        salary_max: formData.get("salary_max"),
      });

      if (!validatedFields.success) {
        const fieldErrors = validatedFields.error.flatten().fieldErrors;
        return {
          message: "Lỗi validation.",
          errors: {
            title: fieldErrors.title ? fieldErrors.title[0] : "",
            jdFile: fieldErrors.jdFile ? fieldErrors.jdFile[0] : "",
            location_type: fieldErrors.location_type
              ? fieldErrors.location_type[0]
              : "",
          },
        };
      }

      const { title, jdFile, location_type, required_skills, min_experience_years, salary_min, salary_max } =
        validatedFields.data;

      // Create FormData for file upload
      const serviceFormData = new FormData();
      serviceFormData.append("file", jdFile);
      serviceFormData.append("title", title);
      serviceFormData.append("location_type", location_type);
      
      const parsedSkills = parseSkillsString(required_skills);
      if (parsedSkills) {
        parsedSkills.forEach((skill) => {
          serviceFormData.append("required_skills", skill);
        });
      }
      
      const minExp = parseNumberString(min_experience_years);
      if (minExp !== undefined) {
        serviceFormData.append("min_experience_years", minExp.toString());
      }
      
      const salMin = parseNumberString(salary_min);
      if (salMin !== undefined) {
        serviceFormData.append("salary_min", salMin.toString());
      }
      
      const salMax = parseNumberString(salary_max);
      if (salMax !== undefined) {
        serviceFormData.append("salary_max", salMax.toString());
      }

      const result = await jobService.createJDWithFile(serviceFormData, accessToken);

      revalidatePath("/jobs");
      revalidatePath("/jobs/jd/upload");

      return {
        message: "Job Description đã được tạo thành công!",
        errors: {},
        data: result,
      };
    } else {
      // Text input mode
      const validatedFields = JDTextSchema.safeParse({
        title: formData.get("title"),
        description: formData.get("description"),
        location_type: formData.get("location_type") || "remote",
        required_skills: formData.get("required_skills"),
        min_experience_years: formData.get("min_experience_years"),
        salary_min: formData.get("salary_min"),
        salary_max: formData.get("salary_max"),
      });

      if (!validatedFields.success) {
        const fieldErrors = validatedFields.error.flatten().fieldErrors;
        return {
          message: "Lỗi validation.",
          errors: {
            title: fieldErrors.title ? fieldErrors.title[0] : "",
            description: fieldErrors.description
              ? fieldErrors.description[0]
              : "",
            location_type: fieldErrors.location_type
              ? fieldErrors.location_type[0]
              : "",
          },
        };
      }

      const {
        title,
        description,
        location_type,
        required_skills,
        min_experience_years,
        salary_min,
        salary_max,
      } = validatedFields.data;

      const result = await jobService.createJD(
        {
          title,
          description,
          location_type: location_type as LocationType,
          required_skills: parseSkillsString(required_skills),
          min_experience_years: parseNumberString(min_experience_years),
          salary_min: parseNumberString(salary_min),
          salary_max: parseNumberString(salary_max),
        },
        accessToken
      );

      revalidatePath("/jobs");
      revalidatePath("/jobs/jd/upload");

      return {
        message: "Job Description đã được tạo thành công!",
        errors: {},
        data: result,
      };
    }
  } catch (error: unknown) {
    console.error("Server Action Error:", error);
    let errorMessage = "Đã xảy ra lỗi khi tạo Job Description.";
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      errorMessage = axiosError.response?.data?.detail || errorMessage;
    }
    return {
      message: errorMessage,
      errors: {},
    };
  }
}

export async function getJDListAction(): Promise<JobDescriptionResponse[]> {
  try {
    const accessToken = await getAccessToken();
    return await jobService.getJDList(accessToken);
  } catch (error) {
    console.error("Error fetching JD list:", error);
    return [];
  }
}

export async function getJDAction(
  jdId: string
): Promise<JobDescriptionResponse | null> {
  try {
    const accessToken = await getAccessToken();
    return await jobService.getJD(jdId, accessToken);
  } catch (error) {
    console.error("Error fetching JD:", error);
    return null;
  }
}

export async function getJDParseStatusAction(
  jdId: string
): Promise<JDParseStatusResponse | null> {
  try {
    const accessToken = await getAccessToken();
    return await jobService.getJDParseStatus(jdId, accessToken);
  } catch (error) {
    console.error("Error fetching JD parse status:", error);
    return null;
  }
}

export async function deleteJDAction(
  jdId: string
): Promise<{ success: boolean; message: string }> {
  try {
    const accessToken = await getAccessToken();
    await jobService.deleteJD(jdId, accessToken);
    revalidatePath("/jobs");
    return { success: true, message: "Job Description đã được xóa thành công." };
  } catch (error) {
    console.error("Server Action Delete Error:", error);
    let errorMessage = "Đã xảy ra lỗi khi xóa Job Description.";
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      errorMessage = axiosError.response?.data?.detail || errorMessage;
    }
    return { success: false, message: errorMessage };
  }
}

export async function updateParsedRequirementsAction(
  jdId: string,
  data: Partial<ParsedJDRequirements>
): Promise<{ success: boolean; message: string; data?: JDParseStatusResponse }> {
  try {
    const accessToken = await getAccessToken();
    const result = await jobService.updateParsedRequirements(jdId, data, accessToken);
    revalidatePath(`/jobs/jd/${jdId}`);
    return {
      success: true,
      message: "Yêu cầu đã được cập nhật thành công.",
      data: result,
    };
  } catch (error) {
    console.error("Server Action Update Error:", error);
    let errorMessage = "Đã xảy ra lỗi khi cập nhật yêu cầu.";
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      errorMessage = axiosError.response?.data?.detail || errorMessage;
    }
    return { success: false, message: errorMessage };
  }
}

export async function getCandidatesAction(
  jdId: string,
  params: CandidateQueryParams = {}
): Promise<RankedCandidateListResponse | null> {
  try {
    const accessToken = await getAccessToken();
    return await jobService.getCandidatesForJD(jdId, params, accessToken);
  } catch (error) {
    console.error("Error fetching candidates:", error);
    return null;
  }
}

export interface GetCandidateCVResult {
  success: boolean;
  data?: RecruiterCVAccessResponse;
  error?: string;
  errorCode?: "NOT_FOUND" | "PRIVATE" | "UNKNOWN";
}

export async function getCandidateCVAction(
  jdId: string,
  cvId: string
): Promise<GetCandidateCVResult> {
  try {
    const accessToken = await getAccessToken();
    const data = await jobService.getCandidateCV(jdId, cvId, accessToken);
    return { success: true, data };
  } catch (error) {
    console.error("Error fetching candidate CV:", error);
    
    // Check for specific error codes
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { status?: number; data?: { detail?: string } };
      };
      
      if (axiosError.response?.status === 403) {
        return {
          success: false,
          error: axiosError.response?.data?.detail || "CV is private",
          errorCode: "PRIVATE",
        };
      }
      
      if (axiosError.response?.status === 404) {
        return {
          success: false,
          error: axiosError.response?.data?.detail || "Candidate not found",
          errorCode: "NOT_FOUND",
        };
      }
    }
    
    return {
      success: false,
      error: "Failed to load candidate CV",
      errorCode: "UNKNOWN",
    };
  }
}
