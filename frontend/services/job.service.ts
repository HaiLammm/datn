import { apiClient } from "@/services/api-client";
import {
  JobDescriptionCreate,
  JobDescriptionResponse,
  JDParseStatusResponse,
  ParsedJDRequirements,
  RankedCandidateListResponse,
  CandidateQueryParams,
  RecruiterCVAccessResponse,
  SemanticSearchRequest,
  SearchResultListResponse,
  CandidateCVFromSearchResponse,
  JobMatchResponse,
  ApplicationResponse,
  ApplicationCreate,
  JobRecommendation,
} from "@datn/shared-types";

export const jobService = {
  /**
   * Create a new Job Description
   */
  createJD: async (
    data: JobDescriptionCreate,
    accessToken?: string
  ): Promise<JobDescriptionResponse> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.post<JobDescriptionResponse>(
        "/jobs/jd",
        data,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error creating JD:", error);
      throw error;
    }
  },

  /**
   * Create a new Job Description with file upload
   * Uses native fetch instead of axios for proper FormData handling in Server Actions
   */
  createJDWithFile: async (
    formData: FormData,
    accessToken?: string
  ): Promise<JobDescriptionResponse> => {
    try {
      const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      // Use native fetch for FormData - it handles multipart/form-data correctly
      // Don't set Content-Type - fetch will set it automatically with proper boundary
      const response = await fetch(`${baseURL}/jobs/jd/upload`, {
        method: 'POST',
        headers,
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error('Failed to create JD with file') as Error & {
          response?: { status: number; data: unknown };
        };
        error.response = { status: response.status, data: errorData };
        throw error;
      }

      return await response.json();
    } catch (error) {
      console.error("Error creating JD with file:", error);
      throw error;
    }
  },

  /**
   * Get list of user's Job Descriptions
   */
  getJDList: async (accessToken?: string): Promise<JobDescriptionResponse[]> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      // Backend returns { items: JobDescriptionResponse[], total: number }
      const response = await apiClient.get<{ items: JobDescriptionResponse[]; total: number }>("/jobs/jd", {
        headers,
      });
      return response.data.items;
    } catch (error) {
      console.error("Error fetching JD list:", error);
      throw error;
    }
  },

  /**
   * Get a single Job Description by ID
   */
  getJD: async (
    jdId: string,
    accessToken?: string
  ): Promise<JobDescriptionResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<JobDescriptionResponse>(
        `/jobs/jd/${jdId}`,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching JD:", error);
      throw error;
    }
  },

  /**
   * Delete a Job Description
   */
  deleteJD: async (jdId: string, accessToken?: string): Promise<void> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      await apiClient.delete(`/jobs/jd/${jdId}`, { headers });
    } catch (error) {
      console.error("Error deleting JD:", error);
      throw error;
    }
  },

  /**
   * Get parsing status of a Job Description
   */
  getJDParseStatus: async (
    jdId: string,
    accessToken?: string
  ): Promise<JDParseStatusResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<JDParseStatusResponse>(
        `/jobs/jd/${jdId}/parse-status`,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching JD parse status:", error);
      throw error;
    }
  },

  /**
   * Update parsed requirements of a Job Description
   * Requires Story 3.2.1 backend endpoint
   */
  updateParsedRequirements: async (
    jdId: string,
    data: Partial<ParsedJDRequirements>,
    accessToken?: string
  ): Promise<JDParseStatusResponse> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.patch<JDParseStatusResponse>(
        `/jobs/jd/${jdId}/parsed-requirements`,
        data,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error updating parsed requirements:", error);
      throw error;
    }
  },

  /**
   * Get ranked candidates for a Job Description
   * @param jdId - Job Description ID
   * @param params - Query parameters (limit, offset, min_score)
   * @param accessToken - Optional access token
   * @returns Paginated list of ranked candidates
   */
  getCandidatesForJD: async (
    jdId: string,
    params: CandidateQueryParams = {},
    accessToken?: string
  ): Promise<RankedCandidateListResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const queryParams = new URLSearchParams();
      if (params.limit !== undefined) {
        queryParams.append("limit", params.limit.toString());
      }
      if (params.offset !== undefined) {
        queryParams.append("offset", params.offset.toString());
      }
      if (params.min_score !== undefined) {
        queryParams.append("min_score", params.min_score.toString());
      }
      const queryString = queryParams.toString();
      const url = `/jobs/jd/${jdId}/candidates${queryString ? `?${queryString}` : ""}`;
      const response = await apiClient.get<RankedCandidateListResponse>(url, {
        headers,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching candidates for JD:", error);
      throw error;
    }
  },

  /**
   * Get a candidate's CV details for recruiter access
   * Only returns data if CV is public
   * @param jdId - Job Description ID
   * @param cvId - CV ID
   * @param accessToken - Optional access token
   * @returns CV analysis and match context
   * @throws 403 if CV is private, 404 if not found
   */
  getCandidateCV: async (
    jdId: string,
    cvId: string,
    accessToken?: string
  ): Promise<RecruiterCVAccessResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<RecruiterCVAccessResponse>(
        `/jobs/jd/${jdId}/candidates/${cvId}`,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching candidate CV:", error);
      throw error;
    }
  },

  /**
   * Get the URL to access a candidate's CV file for preview
   * Only accessible if CV is public
   * @param jdId - Job Description ID
   * @param cvId - CV ID
   * @returns URL string for embedding in iframe or object tag
   * @note Uses Next.js API route proxy to handle authentication
   */
  getCandidateCVFileUrl: (jdId: string, cvId: string): string => {
    // Use Next.js API route proxy instead of direct backend URL because:
    // 1. <embed> tag cannot send HttpOnly cookies cross-origin
    // 2. Proxy route reads cookie and forwards as Authorization header to backend
    // 3. Same-origin request ensures cookies are sent automatically
    return `/api/jobs/jd/${jdId}/candidates/${cvId}/file`;
  },

  /**
   * Download a candidate's CV file
   * Only accessible if CV is public
   * @param jdId - Job Description ID
   * @param cvId - CV ID
   * @returns Blob of the file
   * @throws 403 if CV is private, 404 if not found
   * @note Uses Next.js API route proxy for same-origin cookie handling
   */
  downloadCandidateCV: async (
    jdId: string,
    cvId: string
  ): Promise<{ blob: Blob; filename: string }> => {
    try {
      // Use Next.js proxy route (same-origin) - cookies sent automatically
      const response = await fetch(
        `/api/jobs/jd/${jdId}/candidates/${cvId}/file?download=true`,
        {
          method: "GET",
          credentials: "include", // Ensure cookies are sent
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers.get("content-disposition");
      let filename = "cv.pdf";
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      const blob = await response.blob();

      return {
        blob,
        filename,
      };
    } catch (error) {
      console.error("Error downloading candidate CV:", error);
      throw error;
    }
  },

  /**
   * Search for candidates using natural language query
   * @param params - Search parameters (query, limit, offset, min_score)
   * @param accessToken - Optional access token
   * @returns Paginated list of search results with parsed query
   */
  searchCandidates: async (
    params: SemanticSearchRequest,
    accessToken?: string
  ): Promise<SearchResultListResponse> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.post<SearchResultListResponse>(
        "/jobs/search",
        params,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error searching candidates:", error);
      throw error;
    }
  },

  /**
   * Get a candidate's CV details from search results (no JD context)
   * Only returns data if CV is public
   * @param cvId - CV ID
   * @param accessToken - Optional access token
   * @returns CV analysis without JD match context
   * @throws 403 if CV is private, 404 if not found
   */
  getCandidateCVFromSearch: async (
    cvId: string,
    accessToken?: string
  ): Promise<CandidateCVFromSearchResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<CandidateCVFromSearchResponse>(
        `/jobs/candidates/${cvId}`,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching candidate CV from search:", error);
      throw error;
    }
  },

  /**
   * Get the URL to access a candidate's CV file from search results
   * Only accessible if CV is public
   * @param cvId - CV ID
   * @returns URL string for embedding in iframe or object tag
   * @note Uses Next.js API route proxy to handle authentication
   */
  getCandidateCVFromSearchFileUrl: (cvId: string): string => {
    // Use Next.js API route proxy for same-origin cookie handling
    return `/api/jobs/candidates/${cvId}/file`;
  },

  /**
   * Calculate job match score for a CV against a JD (Story 5.7)
   * Server-side version for use in server actions
   * @param jdId - Job Description ID
   * @param cvId - CV ID
   * @param accessToken - Optional access token
   * @returns Job match score response
   */
  calculateJobMatch: async (
    jdId: string,
    cvId: string,
    accessToken?: string
  ): Promise<JobMatchResponse> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.post<JobMatchResponse>(
        `/jobs/jd/${jdId}/match`,
        { cv_id: cvId },
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error calculating job match:", error);
      throw error;
    }
  },

  /**
   * Get public job details
   */
  getJobDetail: async (id: string): Promise<JobDescriptionResponse> => {
    try {
      console.log("Fetching Job Detail for ID:", id);
      // Public endpoint
      const response = await apiClient.get<JobDescriptionResponse>(`/jobs/${id}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching job detail:", error);
      throw error;
    }
  },

  /**
   * Apply to a job
   */
  applyJob: async (
    jobId: string,
    cvId: string,
    coverLetter?: string,
    accessToken?: string
  ): Promise<ApplicationResponse> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }

      const payload: ApplicationCreate = {
        cv_id: cvId,
        cover_letter: coverLetter,
      };

      const response = await apiClient.post<ApplicationResponse>(
        `/jobs/${jobId}/apply`,
        payload,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error applying to job:", error);
      throw error;
    }
  },

  /**
   * Calculate job match score for a CV against a JD (Story 5.7)
   * Client-side version that uses Next.js API route proxy
   * @param jdId - Job Description ID
   * @param cvId - CV ID
   * @returns Job match score response
   * @note Uses Next.js API route proxy for same-origin cookie handling
   */
  calculateJobMatchClient: async (
    jdId: string,
    cvId: string
  ): Promise<JobMatchResponse> => {
    try {
      // Use Next.js proxy route (same-origin) - cookies sent automatically
      const response = await fetch(`/api/jobs/jd/${jdId}/match`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ cv_id: cvId }),
        credentials: "include", // Ensure cookies are sent
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error calculating job match (client):", error);
      throw error;
    }
  },

  /**
   * Get skill suggestions for autocomplete
   * @param query - Skill keyword to search
   * @param limit - Max number of suggestions
   * @returns List of skill suggestions with counts
   */
  getSkillSuggestions: async (query: string, limit: number = 10): Promise<Array<{ skill: string; count: number }>> => {
    try {
      // Use direct axios call since path is under /jobs
      // Or use apiClient if base URL is set to /api/v1
      // apiClient in this file seems to point to backend API
      const response = await apiClient.get('/jobs/skills/autocomplete', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching skill suggestions:", error);
      return [];
    }
  },

  /**
   * Search for jobs using basic search (Story 9.1)
   * Public endpoint - no authentication required
   * @param params - Search parameters (keyword, location, limit, offset)
   * @returns Paginated list of job postings
   */
  searchJobsBasic: async (params: {
    keyword?: string;
    location?: string;
    min_salary?: number;
    max_salary?: number;
    job_types?: string[];
    skills?: string[];
    benefits?: string[];
    limit?: number;
    offset?: number;
  }): Promise<{
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
  }> => {
    try {
      const queryParams = new URLSearchParams();
      if (params.keyword) {
        queryParams.append("keyword", params.keyword);
      }
      if (params.location) {
        queryParams.append("location", params.location);
      }
      if (params.min_salary !== undefined) {
        queryParams.append("min_salary", params.min_salary.toString());
      }
      if (params.max_salary !== undefined) {
        queryParams.append("max_salary", params.max_salary.toString());
      }
      if (params.job_types && params.job_types.length > 0) {
        params.job_types.forEach((type) => {
          queryParams.append("job_types", type);
        });
      }
      if (params.skills && params.skills.length > 0) {
        params.skills.forEach((skill) => {
          queryParams.append("skills", skill);
        });
      }
      if (params.benefits && params.benefits.length > 0) {
        params.benefits.forEach((benefit) => {
          queryParams.append("benefits", benefit);
        });
      }
      if (params.limit !== undefined) {
        queryParams.append("limit", params.limit.toString());
      }
      if (params.offset !== undefined) {
        queryParams.append("offset", params.offset.toString());
      }
      const queryString = queryParams.toString();
      const url = `/jobs/search/basic${queryString ? `?${queryString}` : ""}`;

      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      console.error("Error searching jobs:", error);
      throw error;
    }
  },

  /**
   * Get personalized job recommendations (Story 9.4)
   * @param limit - Max recommendations to return
   * @param accessToken - Optional access token
   */
  getRecommendations: async (
    limit: number = 10,
    accessToken?: string
  ): Promise<JobRecommendation[]> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<JobRecommendation[]>("/jobs/recommendations", {
        params: { limit },
        headers
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      throw error;
    }
  },
};
