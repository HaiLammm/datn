/**
 * Tests for auth utility functions.
 * 
 * These tests verify the role-checking helper functions and session utilities.
 * Note: getSession() cannot be easily unit tested as it requires Next.js cookies,
 * so we focus on the pure utility functions.
 */

import { 
  canAccessCVs, 
  canAccessJobs, 
  canAccessAdmin, 
  getDefaultRedirect,
  getRoleDisplayName 
} from '../auth';

describe('canAccessCVs', () => {
  it('returns true for job_seeker role', () => {
    expect(canAccessCVs('job_seeker')).toBe(true);
  });

  it('returns true for admin role', () => {
    expect(canAccessCVs('admin')).toBe(true);
  });

  it('returns false for recruiter role', () => {
    expect(canAccessCVs('recruiter')).toBe(false);
  });
});

describe('canAccessJobs', () => {
  it('returns true for recruiter role', () => {
    expect(canAccessJobs('recruiter')).toBe(true);
  });

  it('returns true for admin role', () => {
    expect(canAccessJobs('admin')).toBe(true);
  });

  it('returns false for job_seeker role', () => {
    expect(canAccessJobs('job_seeker')).toBe(false);
  });
});

describe('canAccessAdmin', () => {
  it('returns true for admin role', () => {
    expect(canAccessAdmin('admin')).toBe(true);
  });

  it('returns false for job_seeker role', () => {
    expect(canAccessAdmin('job_seeker')).toBe(false);
  });

  it('returns false for recruiter role', () => {
    expect(canAccessAdmin('recruiter')).toBe(false);
  });
});

describe('getDefaultRedirect', () => {
  it('returns /cvs for job_seeker role', () => {
    expect(getDefaultRedirect('job_seeker')).toBe('/cvs');
  });

  it('returns /jobs for recruiter role', () => {
    expect(getDefaultRedirect('recruiter')).toBe('/jobs');
  });

  it('returns /admin for admin role', () => {
    expect(getDefaultRedirect('admin')).toBe('/admin');
  });

  it('returns /dashboard for unknown role', () => {
    // TypeScript may not allow this, but it's good to test the default case
    // @ts-expect-error Testing unknown role
    expect(getDefaultRedirect('unknown')).toBe('/dashboard');
  });
});

describe('getRoleDisplayName', () => {
  it('returns "Job Seeker" for job_seeker role', () => {
    expect(getRoleDisplayName('job_seeker')).toBe('Job Seeker');
  });

  it('returns "Recruiter" for recruiter role', () => {
    expect(getRoleDisplayName('recruiter')).toBe('Recruiter');
  });

  it('returns "Administrator" for admin role', () => {
    expect(getRoleDisplayName('admin')).toBe('Administrator');
  });

  it('returns "User" for unknown role', () => {
    // @ts-expect-error Testing unknown role
    expect(getRoleDisplayName('unknown')).toBe('User');
  });
});

describe('Role Access Matrix', () => {
  /**
   * This test documents the complete role access matrix as per Story 4.1.
   * 
   * | Feature    | job_seeker | recruiter | admin |
   * |------------|------------|-----------|-------|
   * | CVs        | Yes        | No        | Yes   |
   * | Jobs       | No         | Yes       | Yes   |
   * | Admin      | No         | No        | Yes   |
   */
  const roles = ['job_seeker', 'recruiter', 'admin'] as const;
  
  it('job_seeker can only access CVs', () => {
    expect(canAccessCVs('job_seeker')).toBe(true);
    expect(canAccessJobs('job_seeker')).toBe(false);
    expect(canAccessAdmin('job_seeker')).toBe(false);
  });

  it('recruiter can only access Jobs', () => {
    expect(canAccessCVs('recruiter')).toBe(false);
    expect(canAccessJobs('recruiter')).toBe(true);
    expect(canAccessAdmin('recruiter')).toBe(false);
  });

  it('admin can access everything', () => {
    expect(canAccessCVs('admin')).toBe(true);
    expect(canAccessJobs('admin')).toBe(true);
    expect(canAccessAdmin('admin')).toBe(true);
  });

  it('each role has correct default redirect', () => {
    expect(getDefaultRedirect('job_seeker')).toBe('/cvs');
    expect(getDefaultRedirect('recruiter')).toBe('/jobs');
    expect(getDefaultRedirect('admin')).toBe('/admin');
  });
});
