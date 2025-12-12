export interface ExperienceBreakdown {
  total_years: number;
  key_roles: string[];
  industries: string[];
}

export interface CriteriaExplanation {
  completeness: number;
  experience: number;
  skills: number;
  professionalism: number;
}

export interface CVAnalysis {
  id: string;
  cv_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  ai_score: number | null;
  ai_summary: string | null;
  ai_feedback: Record<string, any> | null;
  extracted_skills: string[] | null;
  created_at: string;
  updated_at: string;
  // Enhanced fields (computed from ai_feedback on backend)
  experience_breakdown: ExperienceBreakdown;
  formatting_feedback: string[];
  ats_hints: string[];
  strengths: string[];
  improvements: string[];
  criteria_explanation: CriteriaExplanation;
}

export interface AnalysisStatus {
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  message?: string;
}

export interface CVWithStatus {
  id: string;
  user_id: number;
  filename: string;
  file_path: string;
  uploaded_at: string;
  is_active: boolean;
  analysis_status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
}