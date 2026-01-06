/**
 * Client-side auth utilities
 * 
 * This module provides client-side authentication helpers that work in browser context.
 * Used for client components that need auth functionality.
 */
import { jwtDecode } from 'jwt-decode';
import type { UserRole, Session, SessionUser, JWTPayload } from '@datn/shared-types';

/**
 * Client-side function to get auth token from cookie or localStorage
 * @returns JWT token string or null
 */
export function getClientAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  
  // Try cookie first
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'access_token') {
      return value;
    }
  }
  
  // Fallback to localStorage
  return localStorage.getItem('access_token');
}

/**
 * Get session from client-side token
 * @returns Session object or null
 */
export function getClientSession(): Session | null {
  try {
    const token = getClientAuthToken();
    if (!token) return null;
    
    const decoded = jwtDecode<JWTPayload>(token);
    
    // Check if token is expired
    if (decoded.exp * 1000 < Date.now()) {
      return null;
    }
    
    const user: SessionUser = {
      id: decoded.user_id || decoded.sub, // Handle both user_id and sub
      email: decoded.email,
      role: decoded.role,
    };
    
    return { user };
  } catch (error) {
    console.error('Client session decode error:', error);
    return null;
  }
}

/**
 * Check if a role can access CV-related features.
 * 
 * CVs are accessible to:
 * - job_seeker: Primary users of CV features
 * - admin: Full access to all features
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
 */
export function canAccessJobs(role: UserRole): boolean {
  return role === 'recruiter' || role === 'admin';
}

/**
 * Check if a role can access Admin features.
 * 
 * Admin features are only accessible to admin users.
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
 * Get a user-friendly display name for a role.
 */
export function getRoleDisplayName(role: UserRole): string {
  switch (role) {
    case 'job_seeker':
      return 'Job Seeker';
    case 'recruiter':
      return 'Recruiter';
    case 'admin':
      return 'Admin';
    default:
      return 'Unknown';
  }
}