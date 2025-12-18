import { apiClient } from "@/services/api-client";
import {
  JobDescriptionCreate,
  JobDescriptionResponse,
  JDParseStatusResponse,
  ParsedJDRequirements,
  RankedCandidateListResponse,
  CandidateQueryParams,
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
   */
  createJDWithFile: async (
    formData: FormData,
    accessToken?: string
  ): Promise<JobDescriptionResponse> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      // Don't set Content-Type - let browser set it with boundary for multipart/form-data
      const response = await apiClient.post<JobDescriptionResponse>(
        "/jobs/jd/upload",
        formData,
        { headers }
      );
      return response.data;
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
};
