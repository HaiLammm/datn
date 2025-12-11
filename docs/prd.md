# DATN Brownfield Enhancement PRD

## 1. Intro Project Analysis and Context

### 1.1. Existing Project Overview

#### 1.1.1. Analysis Source
Document-project output available at: `docs/brownfield-architecture.md`

#### 1.1.2. Current Project State
DATN is a full-stack web application designed for job seekers, built with a Python/FastAPI backend and a Next.js/React frontend. The system's current functionality is focused exclusively on a complete and secure user authentication and registration system. Core business features for CV analysis and job matching are planned but not yet implemented.

### 1.2. Available Documentation Analysis
Using existing project analysis from `docs/brownfield-architecture.md`.

- [x] Tech Stack Documentation
- [x] Source Tree/Architecture
- [x] API Documentation
- [x] Technical Debt Documentation
- [ ] Coding Standards (Partially available in agent definition files)
- [ ] UX/UI Guidelines (Partially available; colors and fonts defined)
- [ ] External API Documentation (Not applicable at this stage)
- [x] Other: `PROJECT_BRIEF.md`, `user_story.md`, `epic-1-completion-report.md`

### 1.3. Enhancement Scope Definition

#### 1.3.1. Enhancement Type
*   New Feature Addition
*   Major Feature Modification
*   Integration with New Systems
*   UI/UX Overhaul

#### 1.3.2. Enhancement Description
This enhancement represents a major evolution of the platform. It involves adding new core features (AI-powered CV analysis), fundamentally modifying the application's scope from a basic auth system, and integrating with a new AI system (Ollama). This will be accompanied by a significant UI/UX overhaul to support the new functionality and create a polished, modern user experience.

#### 1.3.3. Impact Assessment
Significant Impact (substantial new code, but fits existing architecture)

### 1.4. Goals and Background Context

#### 1.4.1. Goals
*   Enable job seekers to upload CVs and receive AI-powered analysis and feedback.
*   Empower recruiters to discover and rank candidates through AI-driven semantic search.
*   Provide basic administrative tools for monitoring AI infrastructure and system health.
*   Deliver a modern, intuitive user interface for enhanced user experience.

#### 1.4.2. Background Context
This enhancement is crucial for realizing the core vision of the AI-Powered Recruitment Platform. It addresses critical pain points for both job seekers, who struggle with optimizing their CVs and finding relevant opportunities, and recruiters, who are overwhelmed by irrelevant applications and the 'semantic gap' in candidate matching. By implementing AI-driven CV analysis and candidate discovery, the platform will leverage its existing secure authentication framework to provide intelligent tools that significantly improve the efficiency and effectiveness of the recruitment process.

### 1.5. Change Log

| Change | Date | Version | Description | Author |
| :--- | :--- | :--- | :--- | :--- |
| Initial PRD Draft | 2025-12-10 | 0.1.0 | First draft of the PRD for Core AI and UI/UX enhancements. | John (PM) |

## 2. Requirements

### 2.1. Functional Requirements

*   **FR1:** The system shall allow job seekers to upload CVs in PDF and DOCX formats for parsing.
*   **FR2:** The system shall automatically parse uploaded CVs to extract relevant professional information.
*   **FR3:** The system shall generate a quality score (0-100) for an uploaded CV based on predefined criteria.
*   **FR4:** The system shall provide a summarized overview of the parsed CV content.
*   **FR5:** The system shall perform ATS-compatibility checks and offer formatting recommendations for uploaded CVs.
*   **FR6:** The system shall allow talent seekers to upload a Job Description (JD) for candidate matching.
*   **FR7:** The system shall automatically rank available candidates based on their relevance to an uploaded JD.
*   **FR8:** The system shall enable natural language search for candidates using semantic understanding.
*   **FR9:** The system shall display real-time server resource utilization (GPU/RAM) for AI infrastructure.
*   **FR10:** The system shall monitor and display AI inference latency.
*   **FR11:** The system shall provide access to system logs related to the AI pipeline.
*   **FR12:** The system shall integrate new CV analysis features into the existing user interface while maintaining consistency.
*   **FR13:** The system shall integrate new JD upload and candidate search features into the existing user interface while maintaining consistency.
*   **FR14:** The system shall allow job seekers to delete their uploaded CVs and associated data to ensure data privacy.
*   **FR15:** The system shall display a history list of uploaded CVs and their corresponding analysis results for the logged-in user.

### 2.2. Non Functional Requirements

*   **NFR1:** The CV parsing success rate shall be greater than 95%.
*   **NFR2:** The system shall provide immediate feedback (loading status) to the user upon submission, while the AI analysis processes asynchronously within a reasonable time (e.g., < 30 seconds).
*   **NFR3:** The API response time for critical endpoints (e.g., CV upload, JD upload) shall be under 500ms for 95% of requests.
*   **NFR4:** The system shall maintain the established security controls (e.g., HttpOnly cookies, bcrypt hashing, JWT validation) for all new features.
*   **NFR5:** All processing of sensitive user data, particularly CV and JD content, shall be performed locally using the Ollama LLM to ensure data privacy.
*   **NFR6:** The system shall be capable of handling a growing volume of CV uploads, JD uploads, and AI processing requests.
*   **NFR7:** The system shall handle concurrent AI processing requests using an asynchronous task queue to prevent server overload.
*   **NFR8:** The user interfaces for CV analysis and candidate discovery shall be intuitive and user-friendly.
*   **NFR9:** User feedback mechanisms shall be incorporated to gather insights for continuous UI/UX improvement.
*   **NFR10:** The system shall aim for a minimum uptime of 99%.
*   **NFR11:** Robust error handling and logging mechanisms shall be implemented for all AI processing operations.
*   **NFR12:** All new code for this enhancement shall conform to the project's modular architecture, coding standards, and type-hinting guidelines.

### 2.3. Compatibility Requirements

*   **CR1: Existing API Compatibility:** New API endpoints and services for CV analysis and job matching shall seamlessly integrate with the existing FastAPI API structure, authentication mechanisms, and response formats, specifically under `/api/v1`.
*   **CR2: Database Schema Compatibility:** New database tables for CVs, jobs, and analysis results shall be designed to integrate with the existing PostgreSQL `users` table without breaking existing user data relationships or data integrity.
*   **CR3: UI/UX Consistency:** All new and modified user interface components shall adhere strictly to the established design system (Shadcn/ui, Tailwind CSS, specific color palette, Be Vietnam Pro font) to ensure a cohesive and consistent user experience.
*   **CR4: Integration Compatibility:** The integration of Ollama for AI processing shall be robust and not interfere with the performance or stability of existing backend services.
*   **CR5: System Environment:** The system shall support deployment on Linux environments (Ubuntu 20.04+) or Windows via WSL2 to ensure compatibility with Ollama.
*   **CR6: Hardware Requirements:** The system shall specify minimum hardware specifications for hosting the local LLM (Recommended: 16GB RAM, Dedicated NVIDIA GPU with 6GB+ VRAM) to meet the performance targets.

## 3. User Interface Enhancement Goals

#### 3.1. Integration with Existing UI
New UI elements and components will strictly adhere to the project's established design system, utilizing Shadcn/ui and Tailwind CSS. Integration will prioritize reusability of existing UI components and maintain visual consistency with the defined color palette, typography ('Be Vietnam Pro'), and global styling patterns. The focus will be on extending existing patterns to accommodate new features, rather than introducing new, disparate design languages.

#### 3.2. Modified/New Screens and Views
*   **For Job Seekers:**
    *   **CV Upload and Analysis Page:** A dedicated interface for uploading CVs, triggering analysis, and viewing results (summary, score, feedback).
    *   **CV History Page:** A screen to display a list of previously uploaded CVs and their respective analysis outputs.
*   **For Talent Seekers:**
    *   **JD Upload and Candidate Search Page:** An interface for uploading Job Descriptions, performing semantic candidate searches, and reviewing matched profiles.
*   **For Administrators:**
    *   **Admin Monitoring Dashboard:** A dashboard to display real-time AI resource utilization (GPU/RAM), inference latency, and system logs access.
    *   **User Management Console:** An interface to view a list of users and perform basic actions like banning or suspending accounts.

#### 3.3. UI Consistency Requirements
To maintain UI consistency, all new and modified components shall:
*   Utilize `cn()` for merging Tailwind CSS classes.
*   Avoid inline `style={{}}` attributes and separate CSS files.
*   Strictly adhere to the defined color palette and 'Be Vietnam Pro' typography.
*   Follow established interaction patterns and component usages (e.g., Shadcn/ui button variants, input styles).

## 4. Technical Constraints and Integration Requirements

#### 4.1. Existing Technology Stack
The project currently utilizes the following technologies:
*   **Backend Runtime**: Python 3.x, FastAPI (>=0.104.1)
*   **ORM**: SQLAlchemy (>=2.0.23)
*   **Database**: PostgreSQL with asyncpg driver
*   **Migrations**: Alembic (>=1.13.0)
*   **Email**: FastAPI-Mail (>=1.4.1)
*   **Auth**: python-jose (>=3.3.0), bcrypt (via passlib 4.0.1)
*   **Validation**: Pydantic
*   **Frontend Runtime**: Node.js
*   **Frontend Framework**: Next.js 16.0.5, React 19.2.0
*   **UI Library**: Shadcn/ui, Tailwind CSS ^4
*   **Forms**: React Hook Form ^7.67.0, Zod ^4.1.13
*   **HTTP Client**: Axios ^1.13.2

#### 4.2. Integration Approach
*   **Database Integration Strategy:** New modules will introduce their own SQLAlchemy models and tables, linked to the existing `users` table via foreign keys where applicable. `alembic` will manage schema changes.
*   **API Integration Strategy:** New API endpoints will be added under `/api/v1` within their respective feature modules (e.g., `/api/v1/cvs`, `/api/v1/jobs`), following the established FastAPI router pattern and security practices.
*   **Frontend Integration Strategy:** The frontend will consume new API endpoints via `src/services` using `api-client.ts` and Next.js Server Actions. New UI components will integrate into the `app/` structure, specifically within `features/` directories, adhering to UI consistency requirements (CR3).
*   **AI Integration Strategy:** Ollama will be integrated into the backend as a distinct service layer. For MVP, `FastAPI BackgroundTasks` will be used for asynchronous processing of AI requests (NFR7) to minimize infrastructure complexity.

#### 4.3. Code Organization and Standards
*   **File Structure Approach:** New backend features will reside in dedicated modules (`backend/app/modules/cvs`, `backend/app/modules/jobs`), following the `models.py`, `schemas.py`, `service.py`, `router.py` pattern. Frontend features will be organized under `frontend/features/` with their own components, hooks, types, and actions.
*   **Naming Conventions:** Adhere to Python's `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_CASE` for constants in the backend. Frontend will follow TypeScript/React conventions.
*   **Coding Standards:** Backend will enforce 4-space indentation, type hints, and `async/await` patterns. Frontend will use import aliases, `cn()` for class merging, and avoid direct DOM manipulation in Server Components.
*   **Documentation Standards:** Inline comments for complex logic, docstrings for functions/endpoints, and API documentation for new endpoints.

#### 4.4. Deployment and Operations
*   **Build Process Integration:** Backend remains a Python application (no specific build step). Frontend will continue to use `npm run build` for Next.js production builds.
*   **Deployment Strategy:** Initial deployment will be manual, building upon the existing local development setup. Future CI/CD integration is a post-MVP goal.
*   **Monitoring and Logging:** Integration with the Admin Monitoring Dashboard (FR9, FR10, FR11) will provide insights into AI service health. Standard application logging will be maintained.
*   **Configuration Management:** Environment variables (`.env`) will continue to manage sensitive configurations (e.g., API keys, database credentials, Ollama endpoint).

#### 4.5. Risk Assessment and Mitigation

| Risk | Impact | Likelihood (for MVP) | Mitigation Strategy (for MVP) |
| :--- | :--- | :--- | :--- |
| **AI Model Performance** (latency, quality) | High | Medium | Careful model selection for Ollama, performance testing, asynchronous processing (NFR2), user feedback during processing. |
| **CV Parsing Accuracy** (extraction, interpretation) | High | Medium | Iterative refinement of parsing logic, testing with diverse CV samples, user feedback for improvement. |
| **Scalability for AI Workloads** (concurrent requests) | Medium | High | Implement asynchronous task queueing (NFR7) to manage concurrent requests and prevent server overload. |
| **Data Privacy Violations** (due to LLM integration) | High | Low | Strict adherence to local LLM processing (NFR5), clear data deletion policy (FR14), avoid sending sensitive data to external AI APIs. |
| **Security: Lack of Rate Limiting** | Medium | Medium | Post-MVP: Implement rate limiting on critical endpoints to prevent brute-force attacks. |
| **Security: Weak Password Validation** | Low | Medium | Post-MVP: Enhance password strength validation in frontend and backend. |
| **Technical Debt: No Automated Tests** | Medium | High | Implement critical integration tests for the core AI pipeline during MVP. Comprehensive unit testing remains a Post-MVP goal. |
