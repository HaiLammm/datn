import { test, expect } from '@playwright/test';

test.describe('Bidirectional Chat Messaging', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the Socket.io server for E2E tests
    await page.route('**/socket.io/**', (route) => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ message: 'Socket.io mocked for E2E tests' }),
      });
    });
  });

  test('recruiter can send message to candidate and candidate can reply', async ({ page, context }) => {
    // This test validates the full bidirectional messaging flow:
    // 1. Recruiter sends message
    // 2. Candidate receives and reads message 
    // 3. Candidate replies
    // 4. Recruiter receives reply
    
    // Step 1: Login as recruiter
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'recruiter@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Verify recruiter dashboard loads
    await expect(page).toHaveURL('/dashboard');
    
    // Step 2: Navigate to candidate list and start conversation
    await page.goto('/jobs/jd/123/candidates');
    await page.click('[data-testid="start-conversation-button"]');
    
    // Verify chat window opens
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    
    // Step 3: Send initial message as recruiter
    const initialMessage = 'Hello, I reviewed your CV and am interested in discussing the position.';
    await page.fill('[data-testid="message-input"]', initialMessage);
    await page.click('[data-testid="send-message-button"]');
    
    // Verify message appears in chat
    await expect(page.locator('[data-testid="message"]').last()).toContainText(initialMessage);
    
    // Step 4: Open new tab/context as candidate
    const candidatePage = await context.newPage();
    await candidatePage.goto('/login');
    await candidatePage.fill('[data-testid="email"]', 'candidate@example.com');
    await candidatePage.fill('[data-testid="password"]', 'password123');
    await candidatePage.click('[data-testid="login-button"]');
    
    // Verify candidate can access messages
    await candidatePage.goto('/messages');
    await expect(candidatePage.locator('[data-testid="conversation-list"]')).toBeVisible();
    
    // Step 5: Candidate opens conversation 
    await candidatePage.click('[data-testid="conversation-item"]');
    
    // Verify candidate can see recruiter's message
    await expect(candidatePage.locator('[data-testid="message"]')).toContainText(initialMessage);
    
    // Step 6: Candidate replies
    const replyMessage = 'Thank you for reaching out! I am very interested in learning more about this opportunity.';
    await candidatePage.fill('[data-testid="message-input"]', replyMessage);
    await candidatePage.click('[data-testid="send-message-button"]');
    
    // Verify reply appears in candidate's chat
    await expect(candidatePage.locator('[data-testid="message"]').last()).toContainText(replyMessage);
    
    // Step 7: Verify recruiter receives reply (in real-time via Socket.io)
    // In a real test, this would verify Socket.io real-time delivery
    // For E2E, we verify by refreshing the recruiter's page
    await page.reload();
    await expect(page.locator('[data-testid="message"]').last()).toContainText(replyMessage);
    
    await candidatePage.close();
  });

  test('candidate cannot access other candidates conversations', async ({ page }) => {
    // Test authorization - candidates should only see their own conversations
    
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'candidate2@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Try to access another candidate's conversation directly
    await page.goto('/messages/conversation-id-belonging-to-other-candidate');
    
    // Should be redirected or see error
    await expect(page.locator('text=Not authorized')).toBeVisible();
  });

  test('conversation history persists across page reloads', async ({ page }) => {
    // Test message persistence
    
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'candidate@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    await page.goto('/messages/test-conversation-id');
    
    // Send a message
    const testMessage = 'This message should persist after reload';
    await page.fill('[data-testid="message-input"]', testMessage);
    await page.click('[data-testid="send-message-button"]');
    
    // Verify message appears
    await expect(page.locator('[data-testid="message"]').last()).toContainText(testMessage);
    
    // Reload page
    await page.reload();
    
    // Verify message is still there
    await expect(page.locator('[data-testid="message"]').last()).toContainText(testMessage);
  });

  test('real-time message delivery works under 1 second', async ({ page, context }) => {
    // Test real-time delivery performance
    // This test requires actual Socket.io connection, not mocked
    
    // Skip this test in CI/CD - requires live Socket.io server
    test.skip(process.env.CI === 'true', 'Requires live Socket.io server');
    
    const startTime = Date.now();
    
    // Login as candidate
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'candidate@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Open conversation
    await page.goto('/messages/test-conversation-id');
    
    // Send message and measure time until it appears
    await page.fill('[data-testid="message-input"]', 'Real-time test message');
    await page.click('[data-testid="send-message-button"]');
    
    // Wait for message to appear and measure time
    await page.waitForSelector('[data-testid="message"]:has-text("Real-time test message")');
    const endTime = Date.now();
    const deliveryTime = endTime - startTime;
    
    // Verify delivery time is under 1 second (1000ms)
    expect(deliveryTime).toBeLessThan(1000);
  });

  test('notification appears when candidate logs in with unread messages', async ({ page }) => {
    // Mock API to return unread count
    await page.route('**/api/v1/messages/conversations/unread-count', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ unread_count: 3 }),
      });
    });
    
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'candidate@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Wait for notification to appear
    await expect(page.locator('text=You have 3 new messages')).toBeVisible();
    
    // Click "View Messages" action
    await page.click('text=View Messages');
    
    // Should navigate to messages page
    await expect(page).toHaveURL('/messages');
  });
});