# DATN Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the DATN codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements, specifically the AI-powered CV analysis and job matching features.

### Document Scope

Focused on areas relevant to: "Adding new core features (AI-powered CV analysis), fundamentally modifying the application's scope from a basic auth system, and integrating with a new AI system (Ollama)."

### Change Log

| Date         | Version | Description                 | Author  |
| :----------- | :------ | :----------                 | :------ |
| 2025-12-12   | 1.0     | Initial brownfield analysis | Winston |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

-   **Backend Main Entry**: `backend/app/main.py`
-   **Backend API Router**: `backend/app/api/v1/api.py`
-   **Backend Core Configuration**: `backend/app/core/config.py`
-   **Backend Database Configuration**: `backend/app/core/database.py`
-   **Frontend Main Entry**: `frontend/app/layout.tsx` (App Router)
-   **Frontend API Client**: `frontend/services/api-client.ts`

### Enhancement Impact Areas

-   **CV Upload/Management**: `backend/app/modules/cv/`, `frontend/features/cv/`
-   **AI Analysis Logic**: `backend/app/modules/ai/`
-   **Job Matching/Management**: `backend/app/modules/jobs/` (Currently a placeholder)
-   **Shared Types**: `packages/shared-types/`

## High Level Architecture

### Technical Summary

The DATN project is a full-stack web application following a Client-Server Model. The Backend is built with FastAPI (Python) and PostgreSQL, running on port 8000. The Frontend is a Next.js (React) application, utilizing the App Router, Shadcn/ui, and Tailwind CSS, running on port 3000. Authentication is cookie-based (HttpOnly Cookies). The current enhancement focuses on integrating AI-powered CV analysis via Ollama, adding CV management, and laying groundwork for job matching.

### Actual Tech Stack

| Category         | Technology               | Version      | Notes                                                                                                                  |
| :--------------- | :----------------------- | :----------- | :----------                                                                                                          |
| **Backend**      |                          |              |                                                                                                                        |
| Runtime          | Python                   | 3.x          |                                                                                                                        |
| Framework        | FastAPI                  | >=0.104.1    | High-performance web framework.                                                                                        |
| ASGI Server      | Uvicorn                  | >=0.24.0     |                                                                                                                        |
| ORM              | SQLAlchemy               | >=2.0.23     | Used for database interactions.                                                                                        |
| DB Driver        | Asyncpg                  | >=0.29.0     | Asynchronous PostgreSQL driver.                                                                                        |
| Migrations       | Alembic                  | >=1.13.0     | Database migration tool.                                                                                               |
| Auth             | python-jose, passlib     | >=3.3.0,     | JWT generation/validation, bcrypt password hashing.                                                                    |
| Config/Validation| Pydantic, pydantic-settings | >=2.5.2,     | Data validation and environment variable management.                                                                   |
| AI Integration   | httpx                    | >=0.25.0     | Asynchronous HTTP client for Ollama API calls.                                                                         |
| Text Extraction  | PyMuPDF (fitz)           | >=1.23.0     | PDF text extraction.                                                                                                   |
| Text Extraction  | python-docx              | >=1.1.0      | DOCX text extraction.                                                                                                  |
| Email            | fastapi-mail             | >=1.4.1      | Asynchronous email sending.                                                                                            |
| **Frontend**     |                          |              |                                                                                                                        |
| Runtime          | Node.js                  |              |                                                                                                                        |
| Framework        | Next.js                  | 16.0.5       | App Router, Server Components/Actions strategy.                                                                        |
| UI Library       | Shadcn/ui, Tailwind CSS  | ^4           | Component library and styling framework.                                                                               |
| Icons            | Lucide React             |              | Icon library.                                                                                                          |
| Forms            | react-hook-form, Zod     | ^7.67.0,     | Form management and client-side validation.                                                                            |
| HTTP Client      | Axios                    | ^1.13.2      | Configured via `api-client.ts`.                                                                                        |

### Repository Structure Reality Check

-   Type: Monorepo (Backend and Frontend are separate projects within the same repository)
-   Package Manager: `npm` (Frontend), `pip` (Backend)
-   Notable: Shared types are defined in `packages/shared-types/`.

## Source Tree and Module Organization

### Project Structure (Actual)

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

### Key Modules and Their Purpose

-   **`auth` (Backend & Frontend)**: Handles user authentication, registration, JWT management (backend), and login/register forms (frontend).
-   **`users` (Backend)**: Manages user profiles and information.
-   **`cv` (Backend)**: Manages CV uploads, storage, database records, and triggers AI analysis. API endpoints are exposed under `/api/v1/cvs`.
-   **`ai` (Backend)**: Contains the core AI logic for CV analysis, integrates with Ollama, extracts text from documents, and provides API endpoints for analysis results and status under `/api/v1/ai/cvs/{cv_id}`.
-   **`jobs` (Backend)**: Currently a placeholder module. Intended for job-related functionalities (creation, matching, search).
-   **`cv` (Frontend)**: Implements the UI and Server Actions for CV management, including upload forms, CV listing, and displaying analysis results.
-   **`shared-types` (Packages)**: Provides common TypeScript type definitions used by both frontend and backend (via code generation/sync) for consistency.

## Data Models and APIs

### Data Models

-   **User Model**: Defined in `backend/app/modules/users/models.py`.
-   **CV Model**: Defined in `backend/app/modules/cv/models.py`. Table name is `cvs`. Linked to `users` via `user_id`.
-   **CVAnalysis Model**: Defined in `backend/app/modules/ai/models.py`. Linked to `cvs` via `cv_id`.
-   Other relevant models (e.g., Job) are yet to be implemented.

### API Specifications

-   **Authentication**:
    -   `POST /api/v1/auth/register`: Register a new user.
    -   `POST /api/v1/auth/login`: Log in to get `access_token` (HttpOnly cookie).
    -   (Other auth endpoints as defined in `backend/GEMINI.md`)
-   **Users**:
    -   `GET /api/v1/users/me`: Get current user's details.
-   **CVs**:
    -   `POST /api/v1/cvs`: Upload a new CV (PDF/DOCX). Trigger AI analysis.
    -   `GET /api/v1/cvs`: Get list of user's uploaded CVs with analysis status.
-   **AI Analysis**:
    -   `GET /api/v1/ai/cvs/{cv_id}/analysis`: Get detailed AI analysis results for a CV.
    -   `GET /api/v1/ai/cvs/{cv_id}/status`: Get current AI analysis status for a CV.
-   **Jobs**: (Currently only a placeholder `GET /api/v1/jobs/` returning `{"message": "This is the jobs router"}`)

## Technical Debt and Known Issues

### Critical Technical Debt

1.  **`jobs` Module**: Currently a complete placeholder in the backend. Full implementation is required for job-related features as per PRD.
2.  **Frontend `ai` Feature**: While the backend `ai` module is strong, a dedicated frontend `ai` feature module might be needed for specific AI-related UI components (e.g., for real-time AI resource monitoring FR9, FR10, FR11). Currently, AI interaction is handled within the `cv` frontend feature.
3.  **Error Handling for AI Analysis**: While `backend/app/modules/ai/service.py` has fallback mechanisms, robust alerting and monitoring for AI service failures (Ollama connectivity, LLM response issues) could be improved.
4.  **Database Migrations**: The project uses Alembic, but the process of creating and applying migrations should be clearly documented and automated for new features.

### Workarounds and Gotchas

-   **HttpOnly Cookie Handling**: Frontend Server Actions must explicitly extract `access_token` from the `cookie` header, as client-side JavaScript cannot access HttpOnly cookies.
-   **Ollama Local Setup**: Users need to have Ollama installed and running locally (or accessible at `OLLAMA_URL`) for the AI analysis to function. Hardware requirements (NVIDIA GPU for performance) are critical.
-   **Frontend `cv_router` prefix**: The backend `cv` module serves endpoints under `/api/v1/cvs`, which is consistent, but it's important to note the `s` in `cvs` for the API path.

## Integration Points and External Dependencies

### External Services

-   **Ollama**: Integrated in `backend/app/modules/ai/service.py` for local LLM inference for CV analysis. Configurable via `OLLAMA_URL` and `LLM_MODEL` in `backend/app/core/config.py`.

### Internal Integration Points

-   **Backend Module Interdependencies**:
    -   `cv` module depends on `users` (for `user_id`) and `ai` (for `CVAnalysis` model and `ai_service`).
    -   `ai` module depends on `cv` (for `CV` model reference) and `users` (for current user context).
-   **Frontend-Backend Communication**:
    -   Frontend Server Actions in `frontend/features/cv/actions.ts` call `cvService` (in `frontend/services/cv.service.ts`).
    -   `cvService` uses `apiClient` (Axios) to make requests to backend endpoints (`/cvs`, `/ai/cvs`).
-   **Background Tasks**: `asyncio.create_task` is used in `backend/app/modules/cv/service.py` to trigger AI analysis in the background.

## Development and Deployment

### Local Development Setup

-   **Backend**: Requires Python environment, `pip install -r requirements.txt`, PostgreSQL database, and Ollama running.
-   **Frontend**: Requires Node.js, `npm install`, and `npm run dev`.
-   Environment variables need to be configured in a `.env` file for the backend.

### Build and Deployment Process

-   **Backend**: No specific build step, runs directly with Uvicorn.
-   **Frontend**: `npm run build` for Next.js production build.
-   Currently, deployment is manual.

## Testing Reality

### Current Test Coverage

-   Unit tests for `auth` and `users` modules are expected, but not explicitly analyzed here.
-   Integration tests for CV upload, AI analysis triggering, and status/results retrieval would be critical.
-   The PRD mentions: "Implement critical integration tests for the core AI pipeline during MVP."

### Running Tests

-   Backend: `pytest` (e.g., `pytest backend/tests/`).
-   Frontend: `jest` (e.g., `npm test`).

## If Enhancement PRD Provided - Impact Analysis

### Files That Will Need Modification

-   **`backend/app/modules/jobs/`**: Full implementation of models, schemas, services, and router.
-   **Frontend UI for Jobs**: New feature module under `frontend/features/jobs/` with corresponding components, actions, and services.
-   **Frontend UI for AI Monitoring**: Potentially a new `frontend/features/ai/` module for admin monitoring dashboard (FR9, FR10, FR11).
-   **`backend/app/main.py`**: Potentially include new routers (e.g., for admin monitoring).
-   **`backend/app/api/v1/api.py`**: Include `jobs_router` and potentially other new routers.
-   **`packages/shared-types/`**: Add new types for Job, JobAnalysis, AI Monitoring data.

### New Files/Modules Needed

-   **`backend/app/modules/jobs/`**: `models.py`, `schemas.py`, `service.py`, `router.py`.
-   **`frontend/features/jobs/`**: New components, `actions.ts`, potentially `hooks/`, `types.ts`.
-   **`frontend/services/job.service.ts`**: New service for job-related API calls.
-   Potentially a new `frontend/features/admin/` or `frontend/features/monitoring/` module.

### Integration Considerations

-   **Database Integration**: New tables for jobs will be linked to users and potentially CVs.
-   **AI Integration for Jobs**: Ollama will likely be used for JD analysis and candidate matching (similar to CV analysis). This will involve creating a `JobAnalysis` model and corresponding service logic in the `ai` module or a new `job_ai` module.
-   **Frontend Routing**: New routes will be needed for job seeker and talent seeker dashboards.
-   **Authorization**: New endpoints will need appropriate authorization checks.

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

-   **Backend Development**: `uvicorn app.main:app --reload` (from `backend/app/` directory).
-   **Frontend Development**: `npm run dev` (from `frontend/` directory).
-   **Database Migrations**: `alembic revision --autogenerate -m "description"`, `alembic upgrade head` (from `backend/` directory).
-   **Running Tests**: `pytest` (from `backend/` directory), `npm test` (from `frontend/` directory).
-   **Ollama**: `ollama run llama3.1:8b` (to ensure the model is downloaded and running).