# Source Tree and Module Organization

## Project Structure (Actual)

```text
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── api.py          # Aggregates all module routers for /api/v1
│   │   ├── core/                   # Core infrastructure (config, database, security)
│   │   │   ├── config.py           # Project settings and environment variables
│   │   │   └── database.py         # SQLAlchemy and async session setup
│   │   └── modules/                # Feature-based modules
│   │       ├── ai/                 # AI analysis for CVs (Ollama integration)
│   │       │   ├── models.py       # CVAnalysis SQLAlchemy model
│   │       │   ├── router.py       # API endpoints for AI analysis results/status
│   │       │   ├── schemas.py      # Pydantic schemas for AI analysis
│   │       │   └── service.py      # Core AI analysis logic (Ollama, text extraction)
│   │       ├── auth/               # User authentication (login, register, token management)
│   │       ├── cv/                 # CV management (upload, storage, listing, deletion)
│   │       │   ├── models.py       # CV SQLAlchemy model (table name: 'cvs')
│   │       │   ├── router.py       # API endpoints for CV operations (/cvs)
│   │       │   ├── schemas.py      # Pydantic schemas for CVs
│   │       │   └── service.py      # CV creation, file handling, AI analysis triggering
│   │       ├── jobs/               # Job management (CURRENTLY A PLACEHOLDER)
│   │       │   ├── models.py       # (Empty)
│   │       │   ├── router.py       # Basic placeholder endpoint
│   │       │   ├── schemas.py      # (Empty)
│   │       │   └── service.py      # (Empty)
│   │       └── users/              # User profile management
├── frontend/
│   ├── app/                        # Next.js App Router (pages, layouts)
│   ├── components/
│   │   └── ui/                     # Shadcn/ui shared components
│   ├── features/                   # Business logic modules (feature-first)
│   │   ├── auth/                   # Authentication related components, hooks, actions
│   │   └── cv/                     # CV related components, hooks, Server Actions
│   │       ├── components/         # Feature-specific UI (e.g., CV upload form)
│   │       └── actions.ts          # Server Actions for CV operations (upload, list, analysis)
│   ├── lib/                        # Global Utilities
│   ├── services/                   # API Clients
│   │   ├── api-client.ts           # Axios instance configuration
│   │   └── cv.service.ts           # Service for CV-related API calls
│   └── types/                      # Global Type Definitions
├── packages/
│   └── shared-types/               # Shared TypeScript types/interfaces
└── docs/                           # Project documentation, PRD
```

## Key Modules and Their Purpose

-   **`auth` (Backend & Frontend)**: Handles user authentication, registration, JWT management (backend), and login/register forms (frontend).
-   **`users` (Backend)**: Manages user profiles and information.
-   **`cv` (Backend)**: Manages CV uploads, storage, database records, and triggers AI analysis. API endpoints are exposed under `/api/v1/cvs`.
-   **`ai` (Backend)**: Contains the core AI logic for CV analysis, integrates with Ollama, extracts text from documents, and provides API endpoints for analysis results and status under `/api/v1/ai/cvs/{cv_id}`.
-   **`jobs` (Backend)**: Currently a placeholder module. Intended for job-related functionalities (creation, matching, search).
-   **`cv` (Frontend)**: Implements the UI and Server Actions for CV management, including upload forms, CV listing, and displaying analysis results.
-   **`shared-types` (Packages)**: Provides common TypeScript type definitions used by both frontend and backend (via code generation/sync) for consistency.
