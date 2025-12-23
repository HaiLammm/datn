export interface CV {
  id: string;
  user_id: number;
  filename: string;
  file_path: string;
  uploaded_at: string; // ISO 8601 string
  is_active: boolean;
  is_public: boolean;
}

export interface SkillSuggestionsResponse {
  suggestions: string[];
}