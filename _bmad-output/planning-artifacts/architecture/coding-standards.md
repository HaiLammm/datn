# Coding Standards

## Critical Fullstack Rules

-   **Public and Protected Routes:** The main dashboard route (`/`) **must** be publicly accessible without requiring authentication. All other application routes (e.g., `/cvs/upload`, `/profile`) **must** be protected and require a logged-in user. Unauthenticated users attempting to access protected routes **must** be redirected to the login page (`/login`).
-   **Type Sharing:** All TypeScript types and interfaces shared between the frontend and backend API (e.g., data models, API payloads) **must** be defined in the `packages/shared-types` package and imported from there. Do not redefine types in the frontend.
-   **API Calls:** All frontend API interactions **must** be channeled through the centralized `API Service Layer` (`/services`). Never make direct `fetch` or `axios` calls from UI components.
-   **Backend Modularity:** All new backend logic **must** be encapsulated within a feature module in `apps/backend/app/modules/`. Each module must follow the `router.py`, `service.py`, `schemas.py`, `models.py` pattern.
-   **Cookie Security:** Do not attempt to read or write authentication tokens from client-side JavaScript. Rely on `HttpOnly` cookies and the backend to manage the session. The frontend must use `withCredentials: true` (or the equivalent) for all API calls.
-   **Authentication Actions:** All authentication operations (login, register, logout, password reset) **must** be implemented as Next.js Server Actions (`'use server'`). Never call authentication APIs directly from client-side JavaScript. This ensures HttpOnly cookies are properly handled server-side and tokens are never exposed to the browser.
-   **HttpOnly Cookie Access:**
    -   **NEVER** read authentication tokens using `document.cookie` in client components - HttpOnly cookies are not accessible to JavaScript by design (security feature).
    -   **Client Components:** Do NOT check session/auth in client components using `getClientSession()` or `document.cookie` for protected routes. Let the Layout handle server-side auth checks.
    -   **Server Components/Layouts:** Use `getSession()` from `lib/auth.ts` (server-side only) to verify authentication.
    -   **Server Actions:** Use `cookies()` from `next/headers` to read HttpOnly cookies server-side.
    -   **Protected Routes Pattern:**
        ```typescript
        // ❌ WRONG - Client component checking auth
        "use client";
        export default function Page() {
          const session = getClientSession(); // Won't work with HttpOnly cookies
          if (!session) router.push("/login"); // Will always redirect
        }

        // ✅ CORRECT - Layout checks auth server-side
        // layout.tsx (Server Component)
        export default async function Layout({ children }) {
          const session = await getSession(); // Server-side cookie access
          if (!session) redirect("/login");
          return children;
        }
        
        // page.tsx (Client Component)
        "use client";
        export default function Page() {
          // No auth check needed - Layout already protected
          // Just fetch data using Server Actions
          const data = await fetchDataAction();
        }
        ```
    -   **Data Fetching with Auth:** All authenticated API calls from client components **must** use Server Actions that read cookies server-side.
-   **Environment Variables:** Access environment variables only through a dedicated configuration module (e.g., `app/core/config.py` in the backend). Never access `process.env` directly within frontend components or backend business logic.
-   **State Updates:** In React components, never mutate state directly. Always use the setter function from `useState` or dispatch actions for reducers.

## SQLAlchemy Async Rules

When working with SQLAlchemy in an async environment, follow these rules to avoid `MissingGreenlet` errors and session management issues:

### 1. Store Attribute Values Before Commit

**Problem:** After calling `db.commit()`, SQLAlchemy will **expire** all objects in the session. If you access an attribute after commit, SQLAlchemy will attempt to lazy-load from the database, causing errors in async context.

```python
# ❌ WRONG - Accessing attribute after commit
async def update_item(item_id: int, current_user: User, db: AsyncSession):
    item = await get_item(db, item_id)
    item.status = "updated"
    await db.commit()
    
    # ERROR: current_user.email will trigger lazy-load after session expired
    logger.info(f"Updated by {current_user.email}")

# ✅ CORRECT - Store value before commit
async def update_item(item_id: int, current_user: User, db: AsyncSession):
    user_email = current_user.email  # Store before commit
    
    item = await get_item(db, item_id)
    item.status = "updated"
    await db.commit()
    
    logger.info(f"Updated by {user_email}")  # Use stored variable
```

### 2. Use Eager Loading for Relationships

**Problem:** Lazy-loaded relationships do not work in async context after the query has completed.

```python
# ❌ WRONG - Lazy loading relationship
async def get_user_with_cvs(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    
    # ERROR: user.cvs will trigger lazy-load
    return {"user": user, "cv_count": len(user.cvs)}

# ✅ CORRECT - Eager loading with selectinload
from sqlalchemy.orm import selectinload

async def get_user_with_cvs(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(User)
        .options(selectinload(User.cvs))  # Load CVs together with User
        .where(User.id == user_id)
    )
    user = result.scalar_one()
    
    return {"user": user, "cv_count": len(user.cvs)}  # OK
```

### 3. Refresh Object After Commit If Continued Use Is Needed

```python
# ✅ CORRECT - Refresh to reload fresh data
async def create_item(data: ItemCreate, db: AsyncSession):
    item = Item(**data.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)  # Reload item with fresh data from DB
    
    return item  # OK - item has been refreshed
```

### 4. Do Not Pass ORM Objects Outside Session Context

```python
# ❌ WRONG - Returning ORM object that may be accessed after session closes
async def get_user(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one()  # Dangerous if caller accesses lazy attributes

# ✅ CORRECT - Convert to Pydantic model or dict
async def get_user(user_id: int, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    return UserResponse.model_validate(user)  # Safe - converted to Pydantic
```

### 5. Quick Reference

| Scenario | Solution |
|----------|----------|
| Need attribute after `commit()` | Store in variable before commit |
| Need to access relationship | Use `selectinload()` or `joinedload()` |
| Need to use object after commit | Call `await db.refresh(obj)` |
| Return data from function | Convert to Pydantic model |

## Code Reusability and Refactoring Standards

### 1. DRY Principle - Don't Repeat Yourself

When implementing new features, **always check for existing similar functionality** before writing new code. If similar logic exists:

1. **Extract common logic** into a shared hook, utility, or component
2. **Refactor existing code** to use the shared abstraction
3. **Document the shared component** with clear usage examples

### 2. Frontend Component Hierarchy

Follow this hierarchy when creating reusable components:

```
┌─────────────────────────────────────────────────────────────────┐
│  lib/hooks/                                                     │
│  - Custom hooks for shared stateful logic                       │
│  - Example: useFileDownload, useDebounce, usePagination         │
├─────────────────────────────────────────────────────────────────┤
│  components/common/                                             │
│  - Generic, reusable UI components                              │
│  - No business logic, only presentation + basic behavior        │
│  - Example: DownloadButton, LoadingSpinner, ConfirmDialog       │
├─────────────────────────────────────────────────────────────────┤
│  features/{feature}/components/                                 │
│  - Feature-specific wrappers around common components           │
│  - Contains business logic, API URLs, error messages            │
│  - Example: DownloadCVButton (wraps DownloadButton)             │
├─────────────────────────────────────────────────────────────────┤
│  app/{route}/                                                   │
│  - Page components that compose feature components              │
│  - Handles routing, layout, data fetching                       │
└─────────────────────────────────────────────────────────────────┘
```

### 3. When to Create Shared Components

Create a shared component when:

| Criteria | Threshold |
|----------|-----------|
| Same UI pattern appears in | 2+ places |
| Same logic/behavior appears in | 2+ places |
| Component has no feature-specific dependencies | Yes |
| Can be configured via props | Yes |

### 4. Shared Component Design Guidelines

```typescript
// ✅ GOOD - Configurable, reusable component
interface DownloadButtonProps {
  downloadUrl: string;           // Required - what to download
  filename: string;              // Required - save as name
  variant?: "icon" | "button";   // Optional - visual style
  buttonText?: string;           // Optional - customizable text
  errorMessages?: {              // Optional - custom error messages
    401?: string;
    403?: string;
    404?: string;
  };
}

// ❌ BAD - Hardcoded, not reusable
interface DownloadCVButtonProps {
  cvId: string;  // Only works for CVs
}
// This component has hardcoded URL: `/api/cvs/${cvId}/download`
```

### 5. API Proxy Routes for Cross-Origin Authentication

**Problem:** HttpOnly cookies are not sent in cross-origin fetch requests.

**Solution:** Create Next.js API proxy routes for authenticated file downloads/uploads.

```
Frontend (port 3000)          Next.js API Route              Backend (port 8000)
       │                            │                              │
       │  fetch("/api/cvs/1/download")                             │
       │  ✓ Cookie sent (same-origin)                              │
       │ ──────────────────────────► │                             │
       │                             │  1. Read access_token       │
       │                             │     from cookies            │
       │                             │                             │
       │                             │  fetch(backend_url, {       │
       │                             │    Authorization: Bearer... │
       │                             │  })                         │
       │                             │ ───────────────────────────►│
       │                             │                             │
       │                             │ ◄─────── File Response ─────│
       │ ◄─── Forward Response ──────│                             │
```

**Proxy route location:** `frontend/app/api/{resource}/[id]/{action}/route.ts`

**Existing proxy routes:**
- `/api/cvs/[cvId]/download` - Job Seeker CV download
- `/api/jobs/candidates/[cvId]/file` - Recruiter view candidate CV (search context)
- `/api/jobs/jd/[jdId]/candidates/[cvId]/file` - Recruiter view candidate CV (JD context)

### 6. Refactoring Checklist

Before adding new functionality, verify:

- [ ] Does similar functionality exist elsewhere in the codebase?
- [ ] Can the existing code be extracted into a shared component/hook?
- [ ] If creating new shared code, is it properly generalized (no hardcoded values)?
- [ ] Are there proper TypeScript interfaces with optional customization props?
- [ ] Is the shared code documented with usage examples?
- [ ] Are existing usages refactored to use the new shared code?

### 7. Example: File Download Refactoring

**Before (duplicated logic):**
```
DownloadCVButton.tsx (Job Seeker)     PDFPreviewSection.tsx (Recruiter)
├── useState for loading              ├── useState for loading
├── fetch with credentials            ├── fetch with credentials  
├── blob → URL → anchor click         ├── blob → URL → anchor click
├── error handling                    ├── error handling
└── toast notifications               └── error display
```

**After (shared abstraction):**
```
lib/hooks/useFileDownload.ts          ← Shared download logic
components/common/DownloadButton.tsx  ← Shared UI component
        ▲                   ▲
        │                   │
DownloadCVButton.tsx    PDFPreviewSection.tsx
(thin wrapper)          (uses DownloadButton)
```

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

## Real-time Messaging Flow (Epic 7)

### Conversation Initialization

**Business Rules:**
- Only **Recruiters** can initiate conversations with Job Seekers
- Job Seekers can only **reply** to existing conversations
- Conversations are created in the context of job applications

**Recruiter → Job Seeker Flow:**
```
1. Recruiter navigates to: /jobs/jd/[jdId]/applicants
2. Views list of candidates who applied to their job posting
3. Clicks "Start Chat" button next to a candidate
4. Enters initial message in prompt dialog
5. System calls createConversation(candidateId, message) Server Action
6. Backend creates conversation record (unique per recruiter-candidate pair)
7. System navigates to /messages/[conversationId]
8. Chat window opens with Socket.io connection
9. Job Seeker receives real-time notification
10. Job Seeker can reply from /messages page
```

**Implementation Pattern:**
```typescript
// ✅ CORRECT - Applicants page with Server Actions
"use client";
import { getJDAction, getApplicantsAction } from "@/features/jobs/actions";
import { createConversation } from "@/features/messages/actions";

export default function ApplicantsPage() {
  useEffect(() => {
    const fetchData = async () => {
      // Use Server Actions - no document.cookie access
      const jobData = await getJDAction(jdId);
      const applicantsData = await getApplicantsAction(jdId);
      setApplicants(applicantsData.applicants);
    };
    fetchData();
  }, [jdId]);

  const handleStartChat = async (candidateId: number) => {
    const message = prompt("Enter your first message:");
    const conversationId = await createConversation(candidateId, message);
    router.push(`/messages/${conversationId}`);
  };
}
```

**Key Components:**
- **Conversation List:** `/messages` - Shows all conversations for current user
- **Chat Window:** `/messages/[conversationId]` - Real-time chat interface
- **Applicants Page:** `/jobs/jd/[jdId]/applicants` - "Start Chat" entry point
- **Server Actions:** `features/messages/actions.ts` - createConversation, getConversations, etc.

**Socket.io Events:**
- `join-conversation` - User joins conversation room
- `send-message` - Send message to conversation
- `new-message` - Receive message in real-time
- `conversation-updated` - Update conversation list (last message, unread count)

---