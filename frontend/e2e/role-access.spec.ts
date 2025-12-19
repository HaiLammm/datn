/**
 * E2E Tests for Role-Based Access Control (RBAC)
 * 
 * These tests verify that users are correctly redirected based on their role
 * when accessing routes they don't have permission to view.
 * 
 * Test Credentials:
 * - Admin: admin@example.com / admin123
 * - Job Seeker: jobseeker@example.com / test123
 * - Recruiter: recruiter@example.com / test123
 */

import { test, expect, Page } from '@playwright/test';

// Helper function to login as a specific user
async function loginAs(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  
  // Wait for redirect after successful login
  await page.waitForURL(/\/(dashboard|cvs|jobs|admin)/);
}

test.describe('Unauthenticated Access', () => {
  test('unauthenticated user is redirected from /cvs to /login', async ({ page }) => {
    await page.goto('/cvs');
    await expect(page).toHaveURL('/login');
  });

  test('unauthenticated user is redirected from /jobs to /login', async ({ page }) => {
    await page.goto('/jobs');
    await expect(page).toHaveURL('/login');
  });

  test('unauthenticated user is redirected from /admin to /login', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).toHaveURL('/login');
  });

  test('unauthenticated user is redirected from /dashboard to /login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
});

test.describe('Job Seeker Role Access', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'jobseeker@example.com', 'test123');
  });

  test('job_seeker can access /cvs', async ({ page }) => {
    await page.goto('/cvs');
    await expect(page).toHaveURL(/\/cvs/);
    // Should not be redirected
    await expect(page.locator('text=My CVs')).toBeVisible({ timeout: 5000 });
  });

  test('job_seeker is redirected from /jobs to /cvs', async ({ page }) => {
    await page.goto('/jobs');
    // Should be redirected to CVs (job_seeker's home)
    await expect(page).toHaveURL(/\/cvs/);
  });

  test('job_seeker is redirected from /admin to unauthorized or cvs', async ({ page }) => {
    await page.goto('/admin');
    // Should be redirected away from admin
    await expect(page).not.toHaveURL(/\/admin/);
  });

  test('job_seeker can access /dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    // Should see job seeker specific content
    await expect(page.locator('text=CV')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Recruiter Role Access', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'recruiter@example.com', 'test123');
  });

  test('recruiter can access /jobs', async ({ page }) => {
    await page.goto('/jobs');
    await expect(page).toHaveURL(/\/jobs/);
    // Should see job descriptions
    await expect(page.locator('text=Job Descriptions')).toBeVisible({ timeout: 5000 });
  });

  test('recruiter is redirected from /cvs to /jobs', async ({ page }) => {
    await page.goto('/cvs');
    // Should be redirected to Jobs (recruiter's home)
    await expect(page).toHaveURL(/\/jobs/);
  });

  test('recruiter is redirected from /admin to unauthorized or jobs', async ({ page }) => {
    await page.goto('/admin');
    // Should be redirected away from admin
    await expect(page).not.toHaveURL(/\/admin/);
  });

  test('recruiter can access /dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    // Should see recruiter specific content
    await expect(page.locator('text=Job')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Admin Role Access', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'admin123');
  });

  test('admin can access /admin', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).toHaveURL(/\/admin/);
    // Should see admin panel
    await expect(page.locator('text=Admin')).toBeVisible({ timeout: 5000 });
  });

  test('admin can access /cvs', async ({ page }) => {
    await page.goto('/cvs');
    await expect(page).toHaveURL(/\/cvs/);
  });

  test('admin can access /jobs', async ({ page }) => {
    await page.goto('/jobs');
    await expect(page).toHaveURL(/\/jobs/);
  });

  test('admin can access /dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });
});

test.describe('Registration Role Selection', () => {
  test('registration form shows role selection', async ({ page }) => {
    await page.goto('/register');
    
    // Should see role selection options
    await expect(page.locator('text=Job Seeker')).toBeVisible();
    await expect(page.locator('text=Recruiter / HR')).toBeVisible();
  });

  test('job_seeker role is selected by default', async ({ page }) => {
    await page.goto('/register');
    
    // Check that the hidden input has job_seeker value
    const hiddenInput = page.locator('input[name="role"]');
    await expect(hiddenInput).toHaveValue('job_seeker');
  });

  test('can select recruiter role', async ({ page }) => {
    await page.goto('/register');
    
    // Click on Recruiter option
    await page.click('text=Recruiter / HR');
    
    // Check that the hidden input value changed
    const hiddenInput = page.locator('input[name="role"]');
    await expect(hiddenInput).toHaveValue('recruiter');
  });
});

test.describe('Role-Based Navigation', () => {
  test('job_seeker sees CV-related navigation', async ({ page }) => {
    await loginAs(page, 'jobseeker@example.com', 'test123');
    await page.goto('/cvs');
    
    // Should see CV-related links in navigation
    const nav = page.locator('nav, header');
    await expect(nav.locator('text=Dashboard')).toBeVisible({ timeout: 5000 });
    // Should not see Jobs link
    await expect(nav.locator('a:has-text("Job Descriptions")')).not.toBeVisible();
  });

  test('recruiter sees Job-related navigation', async ({ page }) => {
    await loginAs(page, 'recruiter@example.com', 'test123');
    await page.goto('/jobs');
    
    // Should see Job-related links in navigation
    const nav = page.locator('nav, header');
    await expect(nav.locator('text=Dashboard')).toBeVisible({ timeout: 5000 });
  });

  test('admin sees Admin navigation', async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'admin123');
    await page.goto('/admin');
    
    // Should see Admin-related links
    const nav = page.locator('nav, header');
    await expect(nav.locator('text=Admin')).toBeVisible({ timeout: 5000 });
  });
});
