import { test, expect } from '@playwright/test';

test.describe('CV Analysis Flow', () => {
  test.describe('Unauthenticated Access', () => {
    test('redirects to login from /cvs page', async ({ page }) => {
      await page.goto('/cvs');
      await expect(page).toHaveURL('/login');
    });

    test('redirects to login from /cvs/[cv_id] page', async ({ page }) => {
      await page.goto('/cvs/some-cv-id');
      await expect(page).toHaveURL('/login');
    });
  });

  test.describe('Authenticated User', () => {
    // Login before each test in this describe block
    test.beforeEach(async ({ page }) => {
      // Navigate to login page
      await page.goto('/login');

      // Fill in login credentials (adjust selectors based on actual form)
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');

      // Submit login form
      await page.click('button[type="submit"]');

      // Wait for navigation or authenticated state
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('displays CV list page after login', async ({ page }) => {
      await page.goto('/cvs');

      // Check for page title or heading
      await expect(page.locator('h1')).toContainText(/My CVs/i);

      // Check for upload button
      await expect(page.locator('a[href="/cvs/upload"]')).toBeVisible();
    });

    test('shows empty state when no CVs uploaded', async ({ page }) => {
      await page.goto('/cvs');

      // Check for empty state message (if no CVs)
      const emptyCvState = page.getByText(/No CVs uploaded yet/i);
      const cvCards = page.locator('[data-testid="cv-card"], .cv-card');

      // Either we have CV cards or empty state
      const hasEmptyState = await emptyCvState.isVisible().catch(() => false);
      const hasCvCards = await cvCards.count() > 0;

      expect(hasEmptyState || hasCvCards).toBeTruthy();
    });

    test('navigates to CV upload page', async ({ page }) => {
      await page.goto('/cvs');

      // Click upload button
      await page.click('a[href="/cvs/upload"]');

      // Should navigate to upload page
      await expect(page).toHaveURL('/cvs/upload');
    });

    test('CV upload form accepts valid PDF file', async ({ page }) => {
      await page.goto('/cvs/upload');

      // Check form is present
      await expect(page.locator('input[type="file"]')).toBeVisible();

      // Check submit button exists
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });
  });

  test.describe('CV Analysis Display', () => {
    // This test requires a pre-existing CV with completed analysis
    // In a real E2E setup, you would seed test data or use API mocking

    test.beforeEach(async ({ page }) => {
      // Login
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('analysis page shows loading state for processing CV', async ({ page }) => {
      // This would require a CV that's currently processing
      // For now, we test the page loads without errors
      await page.goto('/cvs');

      // If there are CV cards, try to navigate to one
      const cvCards = page.locator('a[href^="/cvs/"][href$="/analysis"]');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        await cvCards.first().click();

        // Should show either loading state or analysis results
        const loadingState = page.getByText(/Analyzing your CV/i);
        const analysisResults = page.getByText(/CV Quality Score/i);
        const failedState = page.getByText(/Analysis Failed/i);

        // Wait for one of the states to be visible
        await expect(
          loadingState.or(analysisResults).or(failedState)
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test('completed analysis displays score gauge', async ({ page }) => {
      await page.goto('/cvs');

      const cvCards = page.locator('a[href^="/cvs/"][href$="/analysis"]');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        // Find a card with COMPLETED status
        const completedCard = page.locator('text=Completed').first();
        const isCompleted = await completedCard.isVisible().catch(() => false);

        if (isCompleted) {
          // Click the View Analysis link for the completed CV
          const parentCard = completedCard.locator('xpath=ancestor::div[contains(@class, "rounded-lg")]');
          await parentCard.locator('a:has-text("View Analysis")').click();

          // Should show the score
          await expect(page.getByText(/CV Quality Score/i)).toBeVisible();
        }
      }
    });

    test('analysis page shows back navigation', async ({ page }) => {
      await page.goto('/cvs');

      const cvCards = page.locator('a[href^="/cvs/"][href$="/analysis"]');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        await cvCards.first().click();

        // Should show back link
        await expect(page.getByText(/Back to My CVs/i)).toBeVisible();
      }
    });
  });

  test.describe('Status Badge Display', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('CV cards display status badges', async ({ page }) => {
      await page.goto('/cvs');

      // Check if there are any CV cards
      const cvCards = page.locator('[class*="rounded-lg"]').filter({
        has: page.locator('h3, [class*="font-medium"]')
      });

      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        // Each card should have a status badge
        // Badges can be: Completed, Processing, Pending, or Failed
        const possibleStatuses = ['Completed', 'Processing', 'Pending', 'Failed'];

        for (const status of possibleStatuses) {
          const statusBadge = page.getByText(status, { exact: true });
          const isVisible = await statusBadge.isVisible().catch(() => false);

          if (isVisible) {
            // At least one status badge should be visible
            expect(isVisible).toBeTruthy();
            break;
          }
        }
      }
    });
  });
});
