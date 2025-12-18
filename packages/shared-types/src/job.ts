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
}

/**
 * Request payload for creating a new job description
 */
export interface JobDescriptionCreate extends JobDescriptionBase {}

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
