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
  SemanticSearchRequest,
  SearchResultListResponse,
  CandidateCVFromSearchResponse,
  JobMatchResponse,
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

/**
 * Extract error message from FastAPI response.
 * FastAPI can return errors in different formats:
 * - String: "Error message"
 * - Array of validation errors: [{type, loc, msg, input}, ...]
 * - Object with detail: {detail: "message"} or {detail: [...]}
 */
function extractErrorMessage(detail: unknown, defaultMessage: string): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    // Pydantic validation errors format: [{type, loc, msg, input}, ...]
    const messages = detail
      .map((err) => {
        if (typeof err === "string") return err;
        if (err && typeof err === "object" && "msg" in err) {
          const loc = Array.isArray(err.loc) ? err.loc.join(".") : "";
          return loc ? `${loc}: ${err.msg}` : String(err.msg);
        }
        return null;
      })
      .filter(Boolean);

    return messages.length > 0 ? messages.join("; ") : defaultMessage;
  }

  if (detail && typeof detail === "object") {
    // If it's an object with a 'msg' property (single validation error)
    if ("msg" in detail) {
      return String((detail as { msg: unknown }).msg);
    }
    // If it's an object with a 'message' property
    if ("message" in detail) {
      return String((detail as { message: unknown }).message);
    }
  }

  return defaultMessage;
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
    const defaultMessage = "Đã xảy ra lỗi khi tạo Job Description.";
    let errorMessage = defaultMessage;

    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: unknown } };
      };
      const detail = axiosError.response?.data?.detail;
      errorMessage = extractErrorMessage(detail, defaultMessage);
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
    const defaultMessage = "Đã xảy ra lỗi khi xóa Job Description.";
    let errorMessage = defaultMessage;
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: unknown } };
      };
      const detail = axiosError.response?.data?.detail;
      errorMessage = extractErrorMessage(detail, defaultMessage);
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
    const defaultMessage = "Đã xảy ra lỗi khi cập nhật yêu cầu.";
    let errorMessage = defaultMessage;
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { detail?: unknown } };
      };
      const detail = axiosError.response?.data?.detail;
      errorMessage = extractErrorMessage(detail, defaultMessage);
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

    // Log detailed error information
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { status?: number; data?: { detail?: unknown } };
      };
      console.error("Response status:", axiosError.response?.status);
      console.error("Response data:", axiosError.response?.data);
    }

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

// ============================================================
// Semantic Search Actions (Story 3.7)
// ============================================================

const SemanticSearchParamsSchema = z.object({
  query: z.string().min(2, "Query phải có ít nhất 2 ký tự"),
  limit: z.number().min(1).max(100).optional(),
  offset: z.number().min(0).optional(),
  min_score: z.number().min(0).max(100).optional(),
});

export type SemanticSearchParams = z.infer<typeof SemanticSearchParamsSchema>;

/**
 * Search for candidates using natural language query
 * @param params - Search parameters (query, limit, offset, min_score)
 * @returns Paginated list of search results with parsed query, or null on error
 */
export async function searchCandidatesAction(
  params: SemanticSearchParams
): Promise<SearchResultListResponse | null> {
  try {
    // Validate params
    const validatedParams = SemanticSearchParamsSchema.safeParse(params);
    if (!validatedParams.success) {
      console.error("Validation error:", validatedParams.error);
      return null;
    }

    const accessToken = await getAccessToken();
    const searchRequest: SemanticSearchRequest = {
      query: validatedParams.data.query,
      limit: validatedParams.data.limit,
      offset: validatedParams.data.offset,
      min_score: validatedParams.data.min_score,
    };
    return await jobService.searchCandidates(searchRequest, accessToken);
  } catch (error) {
    console.error("Error searching candidates:", error);
    return null;
  }
}

export interface GetCandidateCVFromSearchResult {
  success: boolean;
  data?: CandidateCVFromSearchResponse;
  error?: string;
  errorCode?: "NOT_FOUND" | "PRIVATE" | "UNKNOWN";
}

/**
 * Get a candidate's CV details from search results (no JD context)
 * @param cvId - CV ID
 * @returns CV analysis without JD match context
 */
export async function getCandidateCVFromSearchAction(
  cvId: string
): Promise<GetCandidateCVFromSearchResult> {
  try {
    const accessToken = await getAccessToken();
    const data = await jobService.getCandidateCVFromSearch(cvId, accessToken);
    return { success: true, data };
  } catch (error) {
    console.error("Error fetching candidate CV from search:", error);

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

// ============================================================
// Job Match Score Actions (Story 5.7)
// ============================================================

/**
 * Calculate job match score for a CV against a JD
 * @param jdId - Job Description ID
 * @param cvId - CV ID
 * @returns Job match score response or null on error
 */
export async function calculateJobMatchAction(
  jdId: string,
  cvId: string
): Promise<JobMatchResponse | null> {
  try {
    const accessToken = await getAccessToken();
    return await jobService.calculateJobMatch(jdId, cvId, accessToken);
  } catch (error) {
    console.error("Error calculating job match:", error);
    return null;
  }
}

/**
 * Get applicants for a job posting
 * @param jdId - Job Description ID
 * @returns List of applicants or null on error
 */
export async function getApplicantsAction(
  jdId: string
): Promise<{ applicants: any[] } | null> {
  try {
    const accessToken = await getAccessToken();
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/jd/${jdId}/applicants`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      console.error(`Failed to fetch applicants: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching applicants:", error);
    return null;
  }
}

/**
 * Calculate job match scores for multiple CVs in parallel
 * @param jdId - Job Description ID
 * @param cvIds - Array of CV IDs
 * @returns Map of cv_id to job_match_score (null if failed)
 */
export async function calculateJobMatchBatchAction(
  jdId: string,
  cvIds: string[]
): Promise<Map<string, number | null>> {
  const accessToken = await getAccessToken();
  const results = new Map<string, number | null>();

  // Make parallel calls for all CVs
  const promises = cvIds.map(async (cvId) => {
    try {
      const response = await jobService.calculateJobMatch(jdId, cvId, accessToken);
      return { cvId, score: response.job_match_score };
    } catch (error) {
      console.error(`Error calculating job match for CV ${cvId}:`, error);
      return { cvId, score: null };
    }
  });

  const responses = await Promise.all(promises);

  for (const { cvId, score } of responses) {
    results.set(cvId, score);
  }

  return results;
}

// ============================================================
// Basic Job Search Actions (Story 9.1)
// ============================================================

export interface BasicJobSearchParams {
  keyword?: string;
  location?: string;
  min_salary?: number;
  max_salary?: number;
  job_types?: string[];
  skills?: string[];
  benefits?: string[];
  limit?: number;
  offset?: number;
}

export interface BasicJobSearchResult {
  items: Array<{
    id: string;
    title: string;
    description: string;
    location_type: string;
    uploaded_at: string;
    salary_min?: number;
    salary_max?: number;
    job_type?: string;
    benefits?: string[];
  }>;
  total: number;
  limit: number;
  offset: number;
}

/**
 * Search for jobs using basic search (public endpoint)
 * @param params - Search parameters (keyword, location, limit, offset)
 * @returns Paginated list of job postings
 */
export async function searchJobsBasicAction(
  params: BasicJobSearchParams
): Promise<BasicJobSearchResult | null> {
  try {
    return await jobService.searchJobsBasic(params);
  } catch (error) {
    console.error("Error searching jobs:", error);
    return null;
  }
}

export interface SkillSuggestion {
  skill: string;
  count: number;
}

export async function getSkillSuggestionsAction(query: string, limit: number = 10): Promise<SkillSuggestion[]> {
  try {
    return await jobService.getSkillSuggestions(query, limit);
  } catch (error) {
    console.error("Error getting skill suggestions:", error);
    return [];
  }
}
