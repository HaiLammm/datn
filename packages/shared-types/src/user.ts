/**
 * User role type for role-based access control
 */
export type UserRole = 'job_seeker' | 'recruiter' | 'admin';

/**
 * User interface representing authenticated user data
 */
export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  avatar?: string;
  birthday?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Session user data extracted from JWT
 */
export interface SessionUser {
  id: string;
  email: string;
  role: UserRole;
}

/**
 * Session object returned by getSession()
 */
export interface Session {
  user: SessionUser;
}

/**
 * User statistics returned by /api/v1/users/me/stats endpoint
 */
export interface UserStats {
  total_cvs: number;
  average_score: number | null;
  best_score: number | null;
  total_unique_skills: number;
  top_skills: string[];
}
