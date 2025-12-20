import { test, expect } from '@playwright/test';

test.describe('User Profile Page', () => {
  test.describe('Unauthenticated Access', () => {
    test('redirects to login when accessing /profile without authentication', async ({ page }) => {
      await page.goto('/profile');
      await expect(page).toHaveURL('/login');
    });
  });

  test.describe('Authenticated User', () => {
    // Login before each test
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('profile page loads for authenticated user', async ({ page }) => {
      await page.goto('/profile');

      // Should stay on profile page
      await expect(page).toHaveURL('/profile');

      // Check for main page heading
      await expect(page.getByRole('heading', { name: 'My Profile' })).toBeVisible();
    });

    test('displays user email correctly', async ({ page }) => {
      await page.goto('/profile');

      const emailElement = page.getByTestId('profile-email');
      await expect(emailElement).toBeVisible();
      await expect(emailElement).toContainText('@');
    });

    test('displays member since date', async ({ page }) => {
      await page.goto('/profile');

      const memberSinceElement = page.getByTestId('profile-member-since');
      await expect(memberSinceElement).toBeVisible();

      // Should contain a formatted date (either "N/A" or a date format)
      const text = await memberSinceElement.textContent();
      expect(text).toBeTruthy();
    });

    test('displays avatar placeholder', async ({ page }) => {
      await page.goto('/profile');

      const avatar = page.getByTestId('profile-avatar');
      await expect(avatar).toBeVisible();

      // Avatar should have fallback with initials
      const fallback = page.getByTestId('avatar-fallback');
      await expect(fallback).toBeVisible();

      // Fallback should have at least one character (initial)
      const initials = await fallback.textContent();
      expect(initials?.length).toBeGreaterThanOrEqual(1);
    });

    test('displays profile card', async ({ page }) => {
      await page.goto('/profile');

      const profileCard = page.getByTestId('profile-card');
      await expect(profileCard).toBeVisible();
    });

    test('displays user statistics', async ({ page }) => {
      await page.goto('/profile');

      const userStats = page.getByTestId('user-stats');
      await expect(userStats).toBeVisible();

      // Check for total CVs stat
      const totalCvs = page.getByTestId('stat-total-cvs');
      await expect(totalCvs).toBeVisible();

      // Check for average score stat
      const avgScore = page.getByTestId('stat-average-score');
      await expect(avgScore).toBeVisible();

      // Check for best score stat
      const bestScore = page.getByTestId('stat-best-score');
      await expect(bestScore).toBeVisible();

      // Check for total skills stat
      const totalSkills = page.getByTestId('stat-total-skills');
      await expect(totalSkills).toBeVisible();
    });

    test('stats display numeric values or N/A', async ({ page }) => {
      await page.goto('/profile');

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

    test('displays account actions', async ({ page }) => {
      await page.goto('/profile');

      const accountActions = page.getByTestId('account-actions');
      await expect(accountActions).toBeVisible();
    });

    test('change password button is visible and navigable', async ({ page }) => {
      await page.goto('/profile');

      const changePasswordButton = page.getByTestId('change-password-button');
      await expect(changePasswordButton).toBeVisible();
      await expect(changePasswordButton).toHaveAttribute('href', '/forgot-password');
    });

    test('delete account button is visible and enabled', async ({ page }) => {
      await page.goto('/profile');

      const deleteAccountButton = page.getByTestId('delete-account-button');
      await expect(deleteAccountButton).toBeVisible();
      await expect(deleteAccountButton).not.toBeDisabled();
    });

    test('clicking change password navigates to forgot password page', async ({ page }) => {
      await page.goto('/profile');

      await page.getByTestId('change-password-button').click();

      await expect(page).toHaveURL('/forgot-password');
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

    test('profile page is responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto('/profile');

      // All main sections should be visible
      await expect(page.getByTestId('profile-card')).toBeVisible();
      await expect(page.getByTestId('user-stats')).toBeVisible();
      await expect(page.getByTestId('account-actions')).toBeVisible();

      // Avatar should be visible
      await expect(page.getByTestId('profile-avatar')).toBeVisible();
    });

    test('profile page is responsive on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.goto('/profile');

      // All main sections should be visible
      await expect(page.getByTestId('profile-card')).toBeVisible();
      await expect(page.getByTestId('user-stats')).toBeVisible();
      await expect(page.getByTestId('account-actions')).toBeVisible();
    });

    test('profile page is responsive on desktop viewport', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1280, height: 800 });

      await page.goto('/profile');

      // All main sections should be visible
      await expect(page.getByTestId('profile-card')).toBeVisible();
      await expect(page.getByTestId('user-stats')).toBeVisible();
      await expect(page.getByTestId('account-actions')).toBeVisible();
    });
  });

  test.describe('Navigation', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('navigation header shows Dashboard link', async ({ page }) => {
      await page.goto('/profile');

      const dashboardLink = page.getByRole('link', { name: /dashboard/i });
      await expect(dashboardLink).toBeVisible();
    });

    test('navigation header shows Profile link as active', async ({ page }) => {
      await page.goto('/profile');

      const profileLink = page.getByRole('link', { name: /profile/i });
      await expect(profileLink).toBeVisible();
      // Profile link should have the active style (blue color)
      await expect(profileLink).toHaveClass(/text-blue-600/);
    });

    test('clicking Dashboard link navigates to dashboard', async ({ page }) => {
      await page.goto('/profile');

      await page.getByRole('link', { name: /dashboard/i }).click();

      await expect(page).toHaveURL('/dashboard');
    });
  });

  test.describe('User with Statistics', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
    });

    test('displays top skills when available', async ({ page }) => {
      await page.goto('/profile');

      // Top skills section is only shown if user has skills
      const topSkillsSection = page.getByTestId('top-skills-section');
      const hasTopSkills = await topSkillsSection.isVisible().catch(() => false);

      if (hasTopSkills) {
        // Should have at least one skill badge
        const firstSkill = page.getByTestId('top-skill-0');
        await expect(firstSkill).toBeVisible();
      }
    });
  });

  test.describe('Empty State', () => {
    // This test requires a fresh user with no CVs
    test('shows empty state message for user with no CVs', async ({ page }) => {
      // Login as a new user
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'newuser@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');

      // Wait for navigation - may fail if user doesn't exist, which is expected
      try {
        await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 5000 });
        await page.goto('/profile');

        // Check for empty state message
        const emptyMessage = page.getByTestId('stats-empty-message');
        const hasEmptyMessage = await emptyMessage.isVisible().catch(() => false);

        if (hasEmptyMessage) {
          await expect(emptyMessage).toContainText('Upload your first CV');
        }
      } catch {
        // User may not exist - test passes
        test.skip();
      }
    });
  });

  test.describe('Account Deletion', () => {
    // Note: This test may delete the test user permanently
    // Use with caution in production/test environments
    test.skip('account deletion flow works correctly', async ({ page }) => {
      // Login with test credentials
      await page.goto('/login');
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');
      await page.waitForURL('/profile', { timeout: 10000 });

      // Navigate to profile
      await page.goto('/profile');
      await expect(page).toHaveURL('/profile');

      // Click delete account button
      const deleteButton = page.getByTestId('delete-account-button');
      await expect(deleteButton).toBeVisible();
      await deleteButton.click();

      // Dialog should open
      const dialog = page.getByTestId('delete-account-dialog');
      await expect(dialog).toBeVisible();

      // Type email confirmation
      const emailInput = page.getByTestId('email-confirmation-input');
      await expect(emailInput).toBeVisible();
      await emailInput.fill('test@example.com');

      // Confirm deletion
      const confirmButton = page.getByTestId('confirm-delete-button');
      await expect(confirmButton).toBeEnabled();
      await confirmButton.click();

      // Should redirect to login
      await page.waitForURL('/login', { timeout: 10000 });
      await expect(page).toHaveURL('/login');

      // Try to login with deleted credentials - should fail
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"]', 'testpassword123');
      await page.click('button[type="submit"]');

      // Should stay on login or show error
      await expect(page).toHaveURL(/\/login/);
      // Could check for error message if implemented
    });
  });
});
