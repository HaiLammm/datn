# Coding Standards

## Critical Fullstack Rules

-   **Public and Protected Routes:** The main dashboard route (`/`) **must** be publicly accessible without requiring authentication. All other application routes (e.g., `/cvs/upload`, `/profile`) **must** be protected and require a logged-in user. Unauthenticated users attempting to access protected routes **must** be redirected to the login page (`/login`).
-   **Type Sharing:** All TypeScript types and interfaces shared between the frontend and backend API (e.g., data models, API payloads) **must** be defined in the `packages/shared-types` package and imported from there. Do not redefine types in the frontend.
-   **API Calls:** All frontend API interactions **must** be channeled through the centralized `API Service Layer` (`/services`). Never make direct `fetch` or `axios` calls from UI components.
-   **Backend Modularity:** All new backend logic **must** be encapsulated within a feature module in `apps/backend/app/modules/`. Each module must follow the `router.py`, `service.py`, `schemas.py`, `models.py` pattern.
-   **Cookie Security:** Do not attempt to read or write authentication tokens from client-side JavaScript. Rely on `HttpOnly` cookies and the backend to manage the session. The frontend must use `withCredentials: true` (or the equivalent) for all API calls.
-   **Environment Variables:** Access environment variables only through a dedicated configuration module (e.g., `app/core/config.py` in the backend). Never access `process.env` directly within frontend components or backend business logic.
-   **State Updates:** In React components, never mutate state directly. Always use the setter function from `useState` or dispatch actions for reducers.

## Naming Conventions

| Element | Frontend Convention | Backend Convention | Example |
| :--- | :--- | :--- | :--- |
| Components (React) | `PascalCase` | N/A | `UserProfile.tsx` |
| Hooks (React) | `camelCase` with `use` prefix | N/A | `useAuth.ts` |
| API Routes | N/A | `kebab-case` | `/api/v1/user-profile` |
| Database Tables | N/A | `snake_case` (plural) | `user_profiles`, `cvs` |
| Python Variables/Functions | N/A | `snake_case` | `get_current_user` |
| Python Classes | N/A | `PascalCase` | `class AuthService:` |
| TypeScript Types/Interfaces | `PascalCase` | N/A | `interface UserProfile {}` |

---