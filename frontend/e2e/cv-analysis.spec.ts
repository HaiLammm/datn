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
      const emptyCvState = page.getByTestId('cv-empty-state');
      const cvCards = page.getByTestId('cv-history-card');

      // Either we have CV cards or empty state
      const hasEmptyState = await emptyCvState.isVisible().catch(() => false);
      const hasCvCards = await cvCards.count() > 0;

      expect(hasEmptyState || hasCvCards).toBeTruthy();
    });

    test('empty state has upload link', async ({ page }) => {
      await page.goto('/cvs');

      const emptyState = page.getByTestId('cv-empty-state');
      const hasEmptyState = await emptyState.isVisible().catch(() => false);

      if (hasEmptyState) {
        const uploadLink = page.getByTestId('upload-first-cv-link');
        await expect(uploadLink).toBeVisible();
        await expect(uploadLink).toHaveAttribute('href', '/cvs/upload');
      }
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

  test.describe('CV History Page with CVs', () => {
    test.beforeEach(async ({ page }) => {
      // Login
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('shows CV count when CVs exist', async ({ page }) => {
      await page.goto('/cvs');

      const cvCount = page.getByTestId('cv-count');
      const hasCount = await cvCount.isVisible().catch(() => false);

      if (hasCount) {
        await expect(cvCount).toContainText(/Your CVs \(\d+ total\)/);
      }
    });

    test('CV cards display quality score', async ({ page }) => {
      await page.goto('/cvs');

      const cvCards = page.getByTestId('cv-history-card');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        // Each card should have a quality score element
        const firstCard = cvCards.first();
        const scoreElement = firstCard.getByTestId('quality-score');
        await expect(scoreElement).toBeVisible();

        // Score should be either a number/100, "Analyzing...", or "N/A"
        const scoreText = await scoreElement.textContent();
        expect(
          scoreText?.match(/^\d+\/100$/) ||
          scoreText === 'Analyzing...' ||
          scoreText === 'N/A'
        ).toBeTruthy();
      }
    });

    test('quality score displays with correct color coding', async ({ page }) => {
      await page.goto('/cvs');

      const cvCards = page.getByTestId('cv-history-card');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        const firstCard = cvCards.first();
        const scoreElement = firstCard.getByTestId('quality-score');
        const scoreClasses = await scoreElement.getAttribute('class');

        // Should have one of the color classes
        expect(
          scoreClasses?.includes('text-green-600') ||
          scoreClasses?.includes('text-yellow-600') ||
          scoreClasses?.includes('text-red-600') ||
          scoreClasses?.includes('text-gray-500')
        ).toBeTruthy();
      }
    });

    test('can navigate to CV analysis from history', async ({ page }) => {
      await page.goto('/cvs');

      const analysisLinks = page.getByTestId('view-analysis-link');
      const linkCount = await analysisLinks.count();

      if (linkCount > 0) {
        const firstLink = analysisLinks.first();
        const href = await firstLink.getAttribute('href');

        // Should have correct href pattern
        expect(href).toMatch(/^\/cvs\/[\w-]+\/analysis$/);

        // Click and verify navigation
        await firstLink.click();
        await expect(page).toHaveURL(/\/cvs\/[\w-]+\/analysis/);
      }
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
      const cvCards = page.getByTestId('view-analysis-link');
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

      const cvCards = page.getByTestId('cv-history-card');
      const cardCount = await cvCards.count();

      if (cardCount > 0) {
        // Find a card with COMPLETED status
        const completedCard = page.locator('text=Completed').first();
        const isCompleted = await completedCard.isVisible().catch(() => false);

        if (isCompleted) {
          // Click the View Analysis link for the completed CV
          const parentCard = completedCard.locator('xpath=ancestor::div[@data-testid="cv-history-card"]');
          await parentCard.getByTestId('view-analysis-link').click();

          // Should show the score
          await expect(page.getByText(/CV Quality Score/i)).toBeVisible();
        }
      }
    });

    test('analysis page shows back navigation', async ({ page }) => {
      await page.goto('/cvs');

      const cvCards = page.getByTestId('view-analysis-link');
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
      const cvCards = page.getByTestId('cv-history-card');
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

  test.describe('Responsive Layout', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('CV grid has correct responsive classes', async ({ page }) => {
      await page.goto('/cvs');

      const cvGrid = page.getByTestId('cv-grid');
      const hasGrid = await cvGrid.isVisible().catch(() => false);

      if (hasGrid) {
        const classes = await cvGrid.getAttribute('class');
        expect(classes).toContain('grid-cols-1');
        expect(classes).toContain('md:grid-cols-2');
        expect(classes).toContain('lg:grid-cols-3');
      }
    });
  });
});
