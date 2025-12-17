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

/**
 * Skill breakdown scores from hybrid skill scoring system.
 * Total score is sum of all sub-scores (0-25 max).
 * @see docs/prd/5-hybrid-skill-scoring-epic.md
 */
export interface SkillBreakdown {
  /** Skill completeness score (0-7): Based on quantity and diversity of skills */
  completeness_score: number;
  /** Category coverage score (0-6): Based on coverage across skill categories */
  categorization_score: number;
  /** Evidence score (0-6): Extracted from LLM analysis (skill usage in experience) */
  evidence_score: number;
  /** Market relevance score (0-6): Based on presence of hot/in-demand skills */
  market_relevance_score: number;
  /** Total skill score (0-25): Sum of all sub-scores */
  total_score: number;
}

/**
 * Categorized skills extracted from CV.
 * Skills are normalized to canonical names and grouped by category.
 * @see docs/prd/5-hybrid-skill-scoring-epic.md
 */
export interface SkillCategories {
  programming_languages: string[];
  frameworks: string[];
  databases: string[];
  devops: string[];
  soft_skills: string[];
  /** AI/ML skills (optional - may not be present in all CVs) */
  ai_ml?: string[];
  /** Other skills that don't fit into predefined categories */
  other: string[];
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
  // Skill breakdown fields (from Story 5.3/5.4 - hybrid skill scoring)
  /** Detailed skill score breakdown (optional - null for older CVs) */
  skill_breakdown?: SkillBreakdown | null;
  /** Categorized skills extracted from CV (optional - null for older CVs) */
  skill_categories?: SkillCategories | null;
  /** AI-generated skill development recommendations (optional - null for older CVs) */
  skill_recommendations?: string[] | null;
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