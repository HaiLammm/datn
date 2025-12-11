# 4. Technical Constraints and Integration Requirements

### 4.1. Existing Technology Stack
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

### 4.2. Integration Approach
*   **Database Integration Strategy:** New modules will introduce their own SQLAlchemy models and tables, linked to the existing `users` table via foreign keys where applicable. `alembic` will manage schema changes.
*   **API Integration Strategy:** New API endpoints will be added under `/api/v1` within their respective feature modules (e.g., `/api/v1/cvs`, `/api/v1/jobs`), following the established FastAPI router pattern and security practices.
*   **Frontend Integration Strategy:** The frontend will consume new API endpoints via `src/services` using `api-client.ts` and Next.js Server Actions. New UI components will integrate into the `app/` structure, specifically within `features/` directories, adhering to UI consistency requirements (CR3).
*   **AI Integration Strategy:** Ollama will be integrated into the backend as a distinct service layer. For MVP, `FastAPI BackgroundTasks` will be used for asynchronous processing of AI requests (NFR7) to minimize infrastructure complexity.

### 4.3. Code Organization and Standards
*   **File Structure Approach:** New backend features will reside in dedicated modules (`backend/app/modules/cvs`, `backend/app/modules/jobs`), following the `models.py`, `schemas.py`, `service.py`, `router.py` pattern. Frontend features will be organized under `frontend/features/` with their own components, hooks, types, and actions.
*   **Naming Conventions:** Adhere to Python's `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_CASE` for constants in the backend. Frontend will follow TypeScript/React conventions.
*   **Coding Standards:** Backend will enforce 4-space indentation, type hints, and `async/await` patterns. Frontend will use import aliases, `cn()` for class merging, and avoid direct DOM manipulation in Server Components.
*   **Documentation Standards:** Inline comments for complex logic, docstrings for functions/endpoints, and API documentation for new endpoints.

### 4.4. Deployment and Operations
*   **Build Process Integration:** Backend remains a Python application (no specific build step). Frontend will continue to use `npm run build` for Next.js production builds.
*   **Deployment Strategy:** Initial deployment will be manual, building upon the existing local development setup. Future CI/CD integration is a post-MVP goal.
*   **Monitoring and Logging:** Integration with the Admin Monitoring Dashboard (FR9, FR10, FR11) will provide insights into AI service health. Standard application logging will be maintained.
*   **Configuration Management:** Environment variables (`.env`) will continue to manage sensitive configurations (e.g., API keys, database credentials, Ollama endpoint).

### 4.5. Risk Assessment and Mitigation

| Risk | Impact | Likelihood (for MVP) | Mitigation Strategy (for MVP) |
| :--- | :--- | :--- | :--- |
| **AI Model Performance** (latency, quality) | High | Medium | Careful model selection for Ollama, performance testing, asynchronous processing (NFR2), user feedback during processing. |
| **CV Parsing Accuracy** (extraction, interpretation) | High | Medium | Iterative refinement of parsing logic, testing with diverse CV samples, user feedback for improvement. |
| **Scalability for AI Workloads** (concurrent requests) | Medium | High | Implement asynchronous task queueing (NFR7) to manage concurrent requests and prevent server overload. |
| **Data Privacy Violations** (due to LLM integration) | High | Low | Strict adherence to local LLM processing (NFR5), clear data deletion policy (FR14), avoid sending sensitive data to external AI APIs. |
| **Security: Lack of Rate Limiting** | Medium | Medium | Post-MVP: Implement rate limiting on critical endpoints to prevent brute-force attacks. |
| **Security: Weak Password Validation** | Low | Medium | Post-MVP: Enhance password strength validation in frontend and backend. |
| **Technical Debt: No Automated Tests** | Medium | High | Implement critical integration tests for the core AI pipeline during MVP. Comprehensive unit testing remains a Post-MVP goal. |
