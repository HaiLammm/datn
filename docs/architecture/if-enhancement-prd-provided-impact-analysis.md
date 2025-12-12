# If Enhancement PRD Provided - Impact Analysis

## Files That Will Need Modification

-   **`backend/app/modules/jobs/`**: Full implementation of models, schemas, services, and router.
-   **Frontend UI for Jobs**: New feature module under `frontend/features/jobs/` with corresponding components, actions, and services.
-   **Frontend UI for AI Monitoring**: Potentially a new `frontend/features/ai/` module for admin monitoring dashboard (FR9, FR10, FR11).
-   **`backend/app/main.py`**: Potentially include new routers (e.g., for admin monitoring).
-   **`backend/app/api/v1/api.py`**: Include `jobs_router` and potentially other new routers.
-   **`packages/shared-types/`**: Add new types for Job, JobAnalysis, AI Monitoring data.

## New Files/Modules Needed

-   **`backend/app/modules/jobs/`**: `models.py`, `schemas.py`, `service.py`, `router.py`.
-   **`frontend/features/jobs/`**: New components, `actions.ts`, potentially `hooks/`, `types.ts`.
-   **`frontend/services/job.service.ts`**: New service for job-related API calls.
-   Potentially a new `frontend/features/admin/` or `frontend/features/monitoring/` module.

## Integration Considerations

-   **Database Integration**: New tables for jobs will be linked to users and potentially CVs.
-   **AI Integration for Jobs**: Ollama will likely be used for JD analysis and candidate matching (similar to CV analysis). This will involve creating a `JobAnalysis` model and corresponding service logic in the `ai` module or a new `job_ai` module.
-   **Frontend Routing**: New routes will be needed for job seeker and talent seeker dashboards.
-   **Authorization**: New endpoints will need appropriate authorization checks.
