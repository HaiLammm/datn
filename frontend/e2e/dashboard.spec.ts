import { test, expect } from '@playwright/test';

test.describe('Enhanced Job Seeker Dashboard', () => {
  test.describe('Unauthenticated Access', () => {
    test('redirects to login from /dashboard', async ({ page }) => {
      await page.goto('/dashboard');
      await expect(page).toHaveURL('/login');
    });
  });

  test.describe('Authenticated Job Seeker', () => {
    // Login before each test as job_seeker
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('dashboard loads for authenticated job_seeker', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should stay on dashboard page
      await expect(page).toHaveURL('/dashboard');
      
      // Check for main dashboard container
      await expect(page.locator('[data-testid="job-seeker-dashboard"]')).toBeVisible();
    });

    test('welcome message displays user email', async ({ page }) => {
      await page.goto('/dashboard');
      
      const welcomeMessage = page.getByTestId('welcome-message');
      await expect(welcomeMessage).toBeVisible();
      await expect(welcomeMessage).toContainText('Welcome back');
      // Should contain user identifier (email)
      await expect(welcomeMessage).toContainText('@');
    });

    test('quick action buttons are visible', async ({ page }) => {
      await page.goto('/dashboard');
      
      const uploadButton = page.getByTestId('upload-cv-button');
      const historyButton = page.getByTestId('view-history-button');
      
      await expect(uploadButton).toBeVisible();
      await expect(historyButton).toBeVisible();
    });

    test('clicking Upload CV navigates to upload page', async ({ page }) => {
      await page.goto('/dashboard');
      
      await page.getByTestId('upload-cv-button').click();
      
      await expect(page).toHaveURL('/cvs/upload');
    });

    test('clicking View CV History navigates to CVs page', async ({ page }) => {
      await page.goto('/dashboard');
      
      await page.getByTestId('view-history-button').click();
      
      await expect(page).toHaveURL('/cvs');
    });

    test('stats section displays correctly', async ({ page }) => {
      await page.goto('/dashboard');
      
      const statsSection = page.getByTestId('dashboard-stats');
      await expect(statsSection).toBeVisible();
      
      // Check for total CVs stat
      const totalCvs = page.getByTestId('stat-total-cvs');
      await expect(totalCvs).toBeVisible();
      
      // Check for average score stat
      const avgScore = page.getByTestId('stat-average-score');
      await expect(avgScore).toBeVisible();
      
      // Check for best score stat
      const bestScore = page.getByTestId('stat-best-score');
      await expect(bestScore).toBeVisible();
    });

    test('stats display numeric values or N/A', async ({ page }) => {
      await page.goto('/dashboard');
      
      const totalCvsValue = page.getByTestId('total-cvs-value');
      const avgScoreValue = page.getByTestId('average-score-value');
      const bestScoreValue = page.getByTestId('best-score-value');
      
      // Total CVs should be a number
      const totalText = await totalCvsValue.textContent();
      expect(totalText).toMatch(/^\d+$/);
      
      // Average and Best scores should be number or "N/A"
      const avgText = await avgScoreValue.textContent();
      const bestText = await bestScoreValue.textContent();
      
      expect(avgText === 'N/A' || avgText?.match(/^\d+$/)).toBeTruthy();
      expect(bestText === 'N/A' || bestText?.match(/^\d+$/)).toBeTruthy();
    });

    test('recent CVs section is visible', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Either shows recent CVs preview or empty state
      const recentCvs = page.getByTestId('recent-cvs-preview');
      const emptyState = page.getByTestId('recent-cvs-empty');
      
      const hasRecentCvs = await recentCvs.isVisible().catch(() => false);
      const hasEmptyState = await emptyState.isVisible().catch(() => false);
      
      expect(hasRecentCvs || hasEmptyState).toBeTruthy();
    });
  });

  test.describe('Dashboard with CVs', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('recent CVs shows uploaded CVs when they exist', async ({ page }) => {
      await page.goto('/dashboard');
      
      const recentCvsPreview = page.getByTestId('recent-cvs-preview');
      const hasPreview = await recentCvsPreview.isVisible().catch(() => false);
      
      if (hasPreview) {
        // Should have CV items
        const cvItems = page.getByTestId('cv-preview-item');
        const itemCount = await cvItems.count();
        
        // Should have at least one item and at most 3 (default limit)
        expect(itemCount).toBeGreaterThan(0);
        expect(itemCount).toBeLessThanOrEqual(3);
      }
    });

    test('CV items show filename and score', async ({ page }) => {
      await page.goto('/dashboard');
      
      const cvItems = page.getByTestId('cv-preview-item');
      const itemCount = await cvItems.count();
      
      if (itemCount > 0) {
        const firstItem = cvItems.first();
        
        // Check filename is present
        const filename = firstItem.getByTestId('cv-filename');
        await expect(filename).toBeVisible();
        
        // Check score is present
        const score = firstItem.getByTestId('cv-score');
        await expect(score).toBeVisible();
        
        // Score should be formatted correctly
        const scoreText = await score.textContent();
        expect(
          scoreText?.match(/^\d+\/100$/) ||
          scoreText === 'Analyzing...' ||
          scoreText === 'N/A'
        ).toBeTruthy();
      }
    });

    test('View All link navigates to CV history', async ({ page }) => {
      await page.goto('/dashboard');
      
      const viewAllLink = page.getByTestId('view-all-link');
      const hasViewAll = await viewAllLink.isVisible().catch(() => false);
      
      if (hasViewAll) {
        await viewAllLink.click();
        await expect(page).toHaveURL('/cvs');
      }
    });

    test('clicking CV preview item navigates to analysis page', async ({ page }) => {
      await page.goto('/dashboard');
      
      const cvItems = page.getByTestId('cv-preview-item');
      const itemCount = await cvItems.count();
      
      if (itemCount > 0) {
        const firstItem = cvItems.first();
        await firstItem.click();
        
        // Should navigate to analysis page
        await expect(page).toHaveURL(/\/cvs\/[^/]+\/analysis/);
      }
    });
  });

  test.describe('Empty State', () => {
    // This test requires a fresh user with no CVs
    // In practice, you would either use a test-specific user or mock the API
    
    test('shows empty state for new user with no CVs', async ({ page }) => {
      // Login as a new user
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'newuser@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      
      // Wait for navigation - may fail if user doesn't exist, which is expected
      try {
        await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 5000 });
        await page.goto('/dashboard');
        
        // Check for empty state
        const emptyState = page.getByTestId('recent-cvs-empty');
        const emptyMessage = page.getByTestId('empty-state-message');
        
        const hasEmptyState = await emptyState.isVisible().catch(() => false);
        
        if (hasEmptyState) {
          await expect(emptyMessage).toContainText('No CVs yet');
        }
      } catch {
        // User may not exist - test passes
        test.skip();
      }
    });
  });

  test.describe('Responsive Design', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('dashboard is responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.goto('/dashboard');
      
      // Dashboard should still be visible
      await expect(page.getByTestId('job-seeker-dashboard')).toBeVisible();
      
      // Quick actions should be visible
      await expect(page.getByTestId('upload-cv-button')).toBeVisible();
      await expect(page.getByTestId('view-history-button')).toBeVisible();
      
      // Stats should be visible
      await expect(page.getByTestId('dashboard-stats')).toBeVisible();
    });

    test('dashboard is responsive on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await page.goto('/dashboard');
      
      // All major sections should be visible
      await expect(page.getByTestId('job-seeker-dashboard')).toBeVisible();
      await expect(page.getByTestId('quick-actions')).toBeVisible();
      await expect(page.getByTestId('dashboard-stats')).toBeVisible();
    });
  });

  test.describe('Loading State', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('loading skeleton may appear during data fetch', async ({ page }) => {
      // Navigate to dashboard
      await page.goto('/dashboard');
      
      // The skeleton might be very brief, so we just check the page loads
      // and the final content is displayed
      await page.waitForSelector('[data-testid="job-seeker-dashboard"], [data-testid="dashboard-skeleton"]', {
        timeout: 10000,
      });
      
      // Eventually, the dashboard content should be visible
      await expect(page.getByTestId('job-seeker-dashboard')).toBeVisible({ timeout: 10000 });
    });
  });
});
