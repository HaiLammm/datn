# Technical Debt and Known Issues

## Critical Technical Debt

1.  **`jobs` Module**: Currently a complete placeholder in the backend. Full implementation is required for job-related features as per PRD.
2.  **Frontend `ai` Feature**: While the backend `ai` module is strong, a dedicated frontend `ai` feature module might be needed for specific AI-related UI components (e.g., for real-time AI resource monitoring FR9, FR10, FR11). Currently, AI interaction is handled within the `cv` frontend feature.
3.  **Error Handling for AI Analysis**: While `backend/app/modules/ai/service.py` has fallback mechanisms, robust alerting and monitoring for AI service failures (Ollama connectivity, LLM response issues) could be improved.
4.  **Database Migrations**: The project uses Alembic, but the process of creating and applying migrations should be clearly documented and automated for new features.

## Workarounds and Gotchas

-   **HttpOnly Cookie Handling**: Frontend Server Actions must explicitly extract `access_token` from the `cookie` header, as client-side JavaScript cannot access HttpOnly cookies.
-   **Ollama Local Setup**: Users need to have Ollama installed and running locally (or accessible at `OLLAMA_URL`) for the AI analysis to function. Hardware requirements (NVIDIA GPU for performance) are critical.
-   **Frontend `cv_router` prefix**: The backend `cv` module serves endpoints under `/api/v1/cvs`, which is consistent, but it's important to note the `s` in `cvs` for the API path.
