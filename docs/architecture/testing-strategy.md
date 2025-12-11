# Testing Strategy

## Testing Pyramid

Our testing strategy will follow the testing pyramid approach, emphasizing a large number of fast, isolated unit tests, a moderate number of integration tests, and a small number of broad end-to-end tests.

```plaintext
          E2E Tests
         /         \
   Integration Tests
  /                 \
Frontend Unit    Backend Unit
```

## Test Organization

Tests will be organized alongside the code they validate, ensuring discoverability and maintainability.

### Frontend Tests
Frontend unit and integration tests (using Jest and React Testing Library) will be co-located with the components or features they test. This means test files will live in the same directory as the source files, often with a `.test.ts` or `.spec.ts` suffix.

```plaintext
frontend/
└── features/
    └── auth/
        ├── components/
        │   ├── LoginForm.tsx
        │   └── LoginForm.test.tsx  # Unit/Integration test for LoginForm
        ├── hooks/
        │   ├── useAuth.ts
        │   └── useAuth.test.ts
        └── actions.ts
```

### Backend Tests
Backend tests (using Pytest and HTTPX) will be organized within a dedicated `apps/backend/tests` directory, mirroring the application's module structure. This makes it easy to find tests for specific services or endpoints.

```plaintext
backend/
└── apps/backend/
    └── tests/
        ├── modules/
        │   ├── auth/
        │   │   └── test_auth_router.py
        │   │   └── test_auth_service.py
        │   └── cvs/
        │       └── test_cv_router.py
        │       └── test_cv_service.py
        └── conftest.py  # Pytest fixtures
```

### E2E Tests
End-to-End (E2E) tests (using Playwright) will reside in a separate top-level `e2e` directory. These tests simulate real user interactions across the entire deployed application.

```plaintext
datn/
└── e2e/
    ├── specs/
    │   ├── auth.spec.ts        # E2E tests for login, registration
    │   └── cv_upload.spec.ts   # E2E tests for CV upload flow
    └── playwright.config.ts
```

## Test Examples

### Frontend Component Test (Jest & React Testing Library)

```typescript
// frontend/features/auth/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from './LoginForm';
import { loginAction } from '../actions'; // Mock this action

// Mock the Server Action
jest.mock('../actions', () => ({
  loginAction: jest.fn(),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    (loginAction as jest.Mock).mockReset();
  });

  it('renders email and password fields', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('calls loginAction with form data on submit', async () => {
    (loginAction as jest.Mock).mockResolvedValueOnce({}); // Mock successful login

    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(loginAction).toHaveBeenCalledTimes(1);
      expect(loginAction).toHaveBeenCalledWith(expect.any(FormData));
      // You can further assert specific FormData content if needed
    });
  });
});
```

### Backend API Test (Pytest & HTTPX)

```python
# backend/apps/backend/tests/modules/auth/test_auth_router.py
import pytest
from httpx import AsyncClient
from main import app # Assuming app instance is importable

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, test_db): # test_db fixture for isolated DB
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200 # Or 201 Created depending on actual implementation
    assert "message" in response.json() # Assuming it returns a success message

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, create_test_user): # create_test_user fixture
    email, password = create_test_user # From fixture

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies # Check for HttpOnly cookie
    assert "refresh_token" in response.cookies
```

### E2E Test (Playwright)

```typescript
// e2e/specs/cv_upload.spec.ts
import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('CV Upload Flow', () => {
  test('should allow a logged-in user to upload a CV', async ({ page }) => {
    // 1. Log in the user
    await page.goto('/login');
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'securepassword123');
    await page.click('button[type="submit"]');

    // Wait for successful login and redirection to dashboard
    await page.waitForURL('/dashboard');
    expect(page.url()).toContain('/dashboard');

    // 2. Navigate to CV Upload page
    await page.click('a[href="/cvs/upload"]');
    await page.waitForURL('/cvs/upload');

    // 3. Upload a CV file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(__dirname, '../test-data/sample_cv.pdf'));

    await page.click('button:has-text("Upload CV")');

    // 4. Verify success message or redirection
    await expect(page.locator('text=CV Uploaded, Analysis Pending...')).toBeVisible();

    // Optionally, wait and check for analysis completion if feasible within E2E
    // await page.waitForSelector('text=Analysis Complete', { timeout: 60000 });
  });
});
```

---