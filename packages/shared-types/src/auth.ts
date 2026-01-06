/**
 * Shared authentication types for JWT tokens and user sessions
 * 
 * These types ensure consistency between frontend and backend JWT handling
 * and follow the BMAD coding standards for shared type definitions.
 */
import type { UserRole } from './user';

/**
 * JWT payload structure used by both frontend and backend
 * 
 * This is the standardized payload that gets encoded in JWT tokens
 * and must be consistent across all modules.
 */
export interface JWTPayload {
  /** User identifier (email address) */
  sub: string;
  
  /** User ID as string */
  user_id: string;
  
  /** User email address */
  email: string;
  
  /** User role for authorization */
  role: UserRole;
  
  /** Token expiration timestamp (Unix timestamp) */
  exp: number;
  
  /** Token type to distinguish access vs refresh tokens */
  type: 'access' | 'refresh';
}

/**
 * User information extracted from JWT token
 * 
 * This is what gets returned after successful JWT verification
 * and is used throughout the application for user context.
 */
export interface JWTUser {
  /** User ID */
  id: string;
  
  /** User email */
  email: string;
  
  /** User role */
  role: UserRole;
}

/**
 * Response from auth verification endpoint
 * 
 * Used by Socket.io server and other services that need
 * to verify JWT tokens via the /auth/verify endpoint.
 */
export interface AuthVerifyResponse {
  /** User ID */
  id: number;
  
  /** User email */
  email: string;
  
  /** User role */
  role: string;
  
  /** User full name (optional) */
  full_name?: string;
  
  /** Whether user account is active */
  is_active: boolean;
}

/**
 * Token pair returned by login endpoint
 */
export interface TokenResponse {
  /** JWT access token */
  access_token: string;
  
  /** Token type (always "bearer") */
  token_type: string;
  
  /** JWT refresh token */
  refresh_token: string;
}

/**
 * Access token response from refresh endpoint
 */
export interface AccessTokenResponse {
  /** JWT access token */
  access_token: string;
  
  /** Token type (always "bearer") */
  token_type: string;
}