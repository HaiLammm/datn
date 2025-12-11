# Frontend Architecture

## Component Architecture

### Component Organization

The frontend code is organized using a **Feature-First (Vertical Slice) Architecture**. This means code is grouped by business domain rather than by type of file.

```plaintext
frontend/
├── app/                  # Next.js App Router (page.tsx, layout.tsx, etc.)
│   ├── (auth)/           # Grouping for authentication-related routes
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   └── layout.tsx
└── features/             # Business Logic Modules
    ├── auth/             # Authentication feature
    │   ├── components/   # Feature-specific UI (LoginForm.tsx, RegisterForm.tsx)
    │   ├── hooks/        # Feature-specific logic (e.g., useAuth)
    │   ├── types.ts      # Local Interfaces & Zod Schemas
    │   └── actions.ts    # Server Actions for auth
    ├── cv/               # CV management feature
    │   ├── components/   # CVUploadForm.tsx, CVList.tsx
    │   └── actions.ts    # Server Actions for CVs
    └── jobs/             # Job/JD management feature
        ├── components/   # JDUploadForm.tsx, JobMatchResults.tsx
        └── actions.ts    # Server Actions for Jobs
```

### Component Template

A standard React functional component template for feature-specific UI components will utilize TypeScript, merge Tailwind CSS classes using `cn()`, and clearly define props.

```typescript
// features/auth/components/LoginForm.tsx
'use client'; // This is a Client Component

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useActionState } from "react";
import { loginAction } from "../actions"; // Assuming an actions.ts file

interface LoginFormProps extends React.ComponentPropsWithoutRef<'form'> {
  // Add specific props for the login form if needed
}

export function LoginForm({ className, ...props }: LoginFormProps) {
  const [state, formAction] = useActionState(loginAction, undefined);

  return (
    <form action={formAction} className={cn("grid gap-4", className)} {...props}>
      <div className="grid gap-2">
        <label htmlFor="email">Email</label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="m@example.com"
          required
        />
        {state?.errors?.email && (
          <p className="text-red-500 text-sm">{state.errors.email}</p>
        )}
      </div>
      <div className="grid gap-2">
        <label htmlFor="password">Password</label>
        <Input
          id="password"
          name="password"
          type="password"
          required
        />
        {state?.errors?.password && (
          <p className="text-red-500 text-sm">{state.errors.password}</p>
        )}
      </div>
      <Button type="submit" className="w-full">
        Login
      </Button>
      {state?.message && (
        <p className="text-red-500 text-sm">{state.message}</p>
      )}
    </form>
  );
}
```

## State Management Architecture

### State Structure

Frontend state management adheres to a layered approach:

-   **Local Component State:** Managed using React's `useState` and `useReducer` hooks for UI-specific data (e.g., form input values, loading indicators within a component).
-   **Form State & Validation:** Handled comprehensively by `react-hook-form` in conjunction with `Zod` for schema validation. This provides robust and efficient form management.
-   **Server Action State:** For forms that submit data via Next.js Server Actions, `useActionState` (React 19) is used. This hook manages the state of the last form submission and any errors, directly integrating with the Server Action's return value.
-   **Global Application State:** For application-wide data (e.g., current authenticated user details, theme settings), React's Context API will be used. This provides a simple and effective way to share state without prop-drilling.

### State Management Patterns

-   `useState` & `useReducer`: For isolated, component-level state.
-   `useContext`: For global, application-wide data that needs to be accessed by many components (e.g., `AuthContext` for user session).
-   `react-hook-form` & `Zod`: For form data management, validation, and submission.
-   `useActionState` (React 19): For handling Server Action responses and managing form submission feedback.
-   `useFormStatus` (React 19): For accessing the pending status of the last form submission within a form.

## Routing Architecture

### Route Organization

The application utilizes **Next.js App Router**, where routing is file-system based. Each folder inside the `app` directory represents a segment of the route, and a `page.tsx` file defines the UI for that route. Routes are logically grouped by feature or user role (e.g., `(auth)`, `dashboard`).

```plaintext
frontend/app/
├── (auth)/                   # Route group for authentication pages
│   ├── login/                # /login
│   │   └── page.tsx
│   ├── register/             # /register
│   │   └── page.tsx
│   └── layout.tsx            # Auth-specific layout
├── dashboard/                # /dashboard
│   └── page.tsx
├── cvs/                      # /cvs (for job seeker)
│   ├── upload/
│   │   └── page.tsx
│   ├── history/
│   │   └── page.tsx
│   └── layout.tsx
├── jobs/                     # /jobs (for talent seeker)
│   ├── jd/
│   │   ├── upload/
│   │   │   └── page.tsx
│   │   └── match/
│   │       └── page.tsx
│   └── layout.tsx
└── layout.tsx                # Root layout
```

### Protected Route Pattern

Protected routes ensure that only authenticated and authorized users can access certain parts of the application. This is typically implemented within `layout.tsx` files or in page components using Next.js Middleware or by performing authentication checks at the Server Component level.

```typescript
// app/dashboard/layout.tsx (Server Component)
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth'; // A server-side function to get session from cookie

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession(); // This function would read the access_token cookie
  if (!session) {
    redirect('/login'); // Redirect unauthenticated users
  }

  // Assuming session object contains user role for authorization
  // if (session.user.role !== 'admin') {
  //   redirect('/unauthorized');
  // }

  return (
    <div className="flex">
      {/* Sidebar, Header, etc. */}
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

## Frontend Services Layer

### API Client Setup

All backend API interactions are centralized in `src/services/api-client.ts`, using `axios`. This client is configured to include credentials automatically, and critically, handles the `access_token` cookie for both client-side and server-side requests.

```typescript
// src/services/api-client.ts
import axios from 'axios';
import { getCookie } from 'cookies-next'; // Example for client-side access, if needed directly

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // IMPORTANT: Automatically includes cookies for client-side requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach cookie for SSR requests (e.g., from Server Actions/Server Components)
// This is a conceptual example and actual implementation depends on how Server Actions
// propagate request headers or contexts. For direct Server Component fetch,
// the cookie would be available in the request headers passed by Next.js.
apiClient.interceptors.request.use(config => {
  if (typeof window === 'undefined') { // Check if running on server-side
    // For Server Components/Actions, we need to manually forward the cookie
    // This is a simplified representation; in reality, the cookie needs to be
    // extracted from the incoming request's headers and explicitly set here.
    // The 'next/headers' module (cookies()) or a context-based approach might be used.
    const accessToken = getCookie('access_token'); // This would need to be from server-side context
    if (accessToken) {
        // Axios's withCredentials handles it, but for explicit control, or
        // if an Authorization header is strictly needed by backend for some reason:
        // config.headers.Authorization = `Bearer ${accessToken}`;
    }
  }
  return config;
});

// Error handling interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Standardized error handling, e.g., redirect to login on 401, show toast for other errors
    if (error.response?.status === 401) {
      // Redirect to login or refresh token logic
      console.error("Unauthorized, redirecting to login...");
      // window.location.href = '/login'; // Client-side redirect
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Service Example

Each feature will have its own service file, abstracting API calls for that domain.

```typescript
// src/services/auth.service.ts
import apiClient from './api-client';
import { LoginPayload, RegisterPayload, User } from '@/types/user'; // Using global types

class AuthService {
  async login(payload: LoginPayload): Promise<User> {
    const response = await apiClient.post('/auth/login', payload);
    return response.data;
  }

  async register(payload: RegisterPayload): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/register', payload);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/users/me');
    return response.data;
  }

  // ... other auth related services
}

export const authService = new AuthService();
```

---