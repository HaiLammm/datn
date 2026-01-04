# Frontend - AI Recruitment Platform

This is the frontend for the AI Recruitment Platform, built with Next.js 14+ (App Router).

## Architecture

The frontend follows a "feature-first" (or "vertical slice") architecture. Code is organized by business features, not by file type.

### Directory Structure

```
├── app/         # Routing (page.tsx, layout.tsx)
├── components/
│   └── ui/      # Shared UI components (from shadcn/ui)
├── features/    # Business logic modules (auth, jobs, etc.)
├── lib/         # Global utilities
├── services/    # API clients for the backend
└── types/       # Global type definitions
```

### Server vs. Client Components

*   `page.tsx` and `layout.tsx` files are always Server Components.
*   Interactive UI is built in "use client" components, which are then imported into server components.

## Design System

The UI is built with `shadcn/ui` and styled with Tailwind CSS.

*   **Color Palette:** A strict color palette is enforced (see `frontend/GEMINI.md` for details).
*   **Typography:** The font is "Be Vietnam Pro".
*   **Styling:** Utility classes are preferred. The `cn()` utility is used to merge classes.

## Tech Stack

*   **Framework:** Next.js (App Router)
*   **UI Library:** `shadcn/ui`
*   **Icons:** Lucide React
*   **Forms:** `react-hook-form` with `zod` for validation.
*   **Styling:** Tailwind CSS

## Data Fetching

*   **Communication with Backend:** All backend communication happens through Server Actions.
*   **No Direct DB Access:** The frontend does not connect directly to the database.
*   **Service Layer:** API calls are abstracted into a service layer (`src/services`).
*   **Authentication:** The frontend relies on HttpOnly cookies set by the backend. API requests are made with `credentials: 'include'`.