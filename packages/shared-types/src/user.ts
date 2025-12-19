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
