import { apiClient } from "@/services/api-client";
import { CV } from "@datn/shared-types";

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
      // In a real application, you might want more sophisticated error handling
      console.error("Error uploading CV:", error);
      throw error;
    }
  },
};
