/**
 * Auth utilities for role-based access control
 * 
 * This module provides server-side session management and role-checking helpers.
 * JWT tokens are stored in HttpOnly cookies and decoded server-side only.
 */
import { cookies } from 'next/headers';
import { jwtDecode } from 'jwt-decode';
import type { UserRole, Session, SessionUser } from '@datn/shared-types';

/**
 * JWT payload structure from the backend
 */
interface JWTPayload {
  sub: string;      // User ID
  email: string;
  role: UserRole;
  exp: number;      // Expiration timestamp
}

/**
 * Get the current session from the JWT cookie.
 * 
 * This function runs on the server and extracts user information from the
 * HttpOnly access_token cookie.
 * 
 * @returns Session object with user data, or null if not authenticated
 */
export async function getSession(): Promise<Session | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;
    
    if (!token) {
      return null;
    }
    
    const decoded = jwtDecode<JWTPayload>(token);
    
    // Check if token is expired
    if (decoded.exp * 1000 < Date.now()) {
      return null;
    }
    
    const user: SessionUser = {
      id: decoded.sub,
      email: decoded.email,
      role: decoded.role,
    };
    
    return { user };
  } catch (error) {
    // Invalid token or decode error
    console.error('Session decode error:', error);
    return null;
  }
}

/**
 * Check if a role can access CV-related features.
 * 
 * CVs are accessible to:
 * - job_seeker: Primary users of CV features
 * - admin: Full access to all features
 * 
 * @param role - The user's role
 * @returns true if the role can access CVs
 */
export function canAccessCVs(role: UserRole): boolean {
  return role === 'job_seeker' || role === 'admin';
}

/**
 * Check if a role can access Job-related features.
 * 
 * Jobs are accessible to:
 * - recruiter: Primary users of job/JD features
 * - admin: Full access to all features
 * 
 * @param role - The user's role
 * @returns true if the role can access Jobs
 */
export function canAccessJobs(role: UserRole): boolean {
  return role === 'recruiter' || role === 'admin';
}

/**
 * Check if a role can access Admin features.
 * 
 * Admin features are only accessible to admin users.
 * 
 * @param role - The user's role
 * @returns true if the role can access Admin
 */
export function canAccessAdmin(role: UserRole): boolean {
  return role === 'admin';
}

/**
 * Get the default redirect path for a role after login.
 * 
 * Each role has a "home" section:
 * - job_seeker: /cvs (CV management)
 * - recruiter: /jobs (Job descriptions and candidate search)
 * - admin: /admin (Admin dashboard)
 * 
 * @param role - The user's role
 * @returns The default redirect path
 */
export function getDefaultRedirect(role: UserRole): string {
  switch (role) {
    case 'job_seeker':
      return '/cvs';
    case 'recruiter':
      return '/jobs';
    case 'admin':
      return '/admin';
    default:
      return '/dashboard';
  }
}

/**
 * Get role display name for UI
 * 
 * @param role - The user's role
 * @returns Human-readable role name
 */
export function getRoleDisplayName(role: UserRole): string {
  switch (role) {
    case 'job_seeker':
      return 'Job Seeker';
    case 'recruiter':
      return 'Recruiter';
    case 'admin':
      return 'Administrator';
    default:
      return 'User';
  }
}
