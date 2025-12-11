import { test, expect } from '@playwright/test';

test('unauthenticated user is redirected from /cvs/upload to /login', async ({ page }) => {
  // Navigate to the CV upload page
  await page.goto('/cvs/upload');

  // Expect to be redirected to the login page
  await expect(page).toHaveURL('/login');
});