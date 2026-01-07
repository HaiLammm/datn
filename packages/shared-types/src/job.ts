/**
 * Job Description types shared between frontend and backend
 */

export type LocationType = "remote" | "hybrid" | "on-site";

/**
 * Parse status for Job Description parsing
 */
export type JDParseStatus = "pending" | "processing" | "completed" | "failed";

/**
 * Parsed requirements extracted from Job Description
 */
export interface ParsedJDRequirements {
  required_skills: string[];
  nice_to_have_skills: string[];
  min_experience_years: number | null;
  job_title_normalized: string | null;
  key_responsibilities: string[];
}

/**
 * Response for JD parse status endpoint
 */
export interface JDParseStatusResponse {
  parse_status: JDParseStatus;
  parsed_requirements: ParsedJDRequirements | null;
  parse_error: string | null;
}

/**
 * Base interface for JobDescription data
 */
export interface JobDescriptionBase {
  title: string;
  description: string;
  required_skills?: string[] | null;
  min_experience_years?: number | null;
  location_type: LocationType;
  salary_min?: number | null;
  salary_max?: number | null;
  benefits?: string[] | null;
  job_type?: string | null;
}

/**
 * Request payload for creating a new job description
 */
export interface JobDescriptionCreate extends JobDescriptionBase { }

/**
 * Response from the API for a single job description
 */
export interface JobDescriptionResponse extends JobDescriptionBase {
  id: string;
  user_id: number;
  uploaded_at: string;
  is_active: boolean;
  parse_status: JDParseStatus;
  parsed_requirements?: ParsedJDRequirements | null;
}

/**
 * Response from the API for listing job descriptions
 */
export interface JobDescriptionList {
  items: JobDescriptionResponse[];
  total: number;
}

/**
 * Match breakdown details for a candidate
 */
export interface MatchBreakdownResponse {
  matched_skills: string[];
  missing_skills: string[];
  extra_skills: string[];
  skill_score: number;
  experience_score: number;
  experience_years: number | null;
  required_experience_years: number | null;
}

/**
 * Response for a single ranked candidate
 */
export interface RankedCandidateResponse {
  cv_id: string;
  user_id: number;
  match_score: number;
  breakdown: MatchBreakdownResponse;
  cv_summary: string | null;
  filename: string | null;
  is_public: boolean;
}

/**
 * Response for listing ranked candidates with pagination
 */
export interface RankedCandidateListResponse {
  items: RankedCandidateResponse[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Query parameters for fetching candidates
 */
export interface CandidateQueryParams {
  limit?: number;
  offset?: number;
  min_score?: number;
}

/**
 * Response for recruiter accessing a candidate's CV
 */
export interface RecruiterCVAccessResponse {
  cv_id: string;
  filename: string;
  uploaded_at: string;
  ai_score: number | null;
  ai_summary: string | null;
  extracted_skills: string[] | null;
  /** Skill breakdown - may be partial or null */
  skill_breakdown: Record<string, number> | null;
  /** Skill categories - may be partial or null */
  skill_categories: Record<string, string[]> | null;
  match_score: number | null;
  matched_skills: string[] | null;
}

// ============================================================
// Semantic Search Types (Story 3.7)
// ============================================================

/**
 * Request payload for semantic candidate search
 */
export interface SemanticSearchRequest {
  query: string; // Natural language query (min 2 chars)
  limit?: number; // Default 20, max 100
  offset?: number; // Default 0
  min_score?: number; // Default 0, range 0-100
}

/**
 * Parsed query interpretation from LLM
 */
export interface ParsedQueryResponse {
  extracted_skills: string[];
  experience_keywords: string[];
  raw_query: string;
}

/**
 * Single search result for a candidate
 */
export interface SearchResultResponse {
  cv_id: string; // UUID
  user_id: number;
  relevance_score: number; // 0-100
  matched_skills: string[];
  cv_summary: string | null;
  filename: string | null;
}

/**
 * Paginated list of search results
 */
export interface SearchResultListResponse {
  items: SearchResultResponse[];
  total: number;
  limit: number;
  offset: number;
  parsed_query: ParsedQueryResponse;
}

/**
 * Response for recruiter accessing a candidate's CV from search (no JD context)
 */
export interface CandidateCVFromSearchResponse {
  cv_id: string;
  filename: string;
  uploaded_at: string;
  ai_score: number | null;
  ai_summary: string | null;
  extracted_skills: string[] | null;
  skill_breakdown: Record<string, number> | null;
  skill_categories: Record<string, string[]> | null;
  is_public: boolean;
}

// ============================================================
// Job Match Score Types (Story 5.7)
// ============================================================

/**
 * Request payload for calculating job match score
 */
export interface JobMatchRequest {
  cv_id: string;
}

/**
 * Response for job match score calculation
 */
export interface JobMatchResponse {
  cv_id: string;
  job_id: string;
  job_match_score: number; // 0-100
}

/**
 * Application types (Story 9.3)
 */
export interface ApplicationBase {
  cover_letter?: string | null;
}

export interface ApplicationCreate extends ApplicationBase {
  cv_id: string;
}

export interface ApplicationResponse extends ApplicationBase {
  id: string;
  job_id: string;
  user_id: number;
  cv_id: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Job Recommendation Response (Story 9.4)
 */
export interface JobRecommendation {
  id: string; // Job ID
  title: string;
  description: string;
  location_type: string;
  salary_min: number | null;
  salary_max: number | null;

  match_score: number; // 0-100
  semantic_score: number; // 0-1
  matched_skills: string[];
  missing_skills: string[];

  uploaded_at: string;
}
