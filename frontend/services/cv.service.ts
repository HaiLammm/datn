import { apiClient } from "@/services/api-client";
import { CV, CVWithStatus, CVAnalysis, AnalysisStatus } from "@datn/shared-types";

export const cvService = {
  uploadCV: async (formData: FormData, accessToken?: string): Promise<CV> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "multipart/form-data",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.post<CV>("/cvs", formData, {
        headers,
      });
      return response.data;
    } catch (error) {
      console.error("Error uploading CV:", error);
      throw error;
    }
  },

  getCVList: async (accessToken?: string): Promise<CVWithStatus[]> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<CVWithStatus[]>("/cvs", { headers });
      return response.data;
    } catch (error) {
      console.error("Error fetching CV list:", error);
      throw error;
    }
  },

  getAnalysis: async (cvId: string, accessToken?: string): Promise<CVAnalysis> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<CVAnalysis>(`/ai/cvs/${cvId}/analysis`, { headers });
      return response.data;
    } catch (error) {
      console.error("Error fetching CV analysis:", error);
      throw error;
    }
  },

  getAnalysisStatus: async (cvId: string, accessToken?: string): Promise<AnalysisStatus> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.get<AnalysisStatus>(`/ai/cvs/${cvId}/status`, { headers });
      return response.data;
    } catch (error) {
      console.error("Error fetching analysis status:", error);
      throw error;
    }
  },

  deleteCV: async (cvId: string, accessToken?: string): Promise<void> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      await apiClient.delete(`/cvs/${cvId}`, { headers });
    } catch (error) {
      console.error("Error deleting CV:", error);
      throw error;
    }
  },

  updateVisibility: async (cvId: string, isPublic: boolean, accessToken?: string): Promise<CVWithStatus> => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }
      const response = await apiClient.patch<CVWithStatus>(
        `/cvs/${cvId}/visibility`,
        { is_public: isPublic },
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error updating CV visibility:", error);
      throw error;
    }
  },
};
