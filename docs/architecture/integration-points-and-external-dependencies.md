# Integration Points and External Dependencies

## External Services

-   **Ollama**: Integrated in `backend/app/modules/ai/service.py` for local LLM inference for CV analysis. Configurable via `OLLAMA_URL` and `LLM_MODEL` in `backend/app/core/config.py`.

## Internal Integration Points

-   **Backend Module Interdependencies**:
    -   `cv` module depends on `users` (for `user_id`) and `ai` (for `CVAnalysis` model and `ai_service`).
    -   `ai` module depends on `cv` (for `CV` model reference) and `users` (for current user context).
-   **Frontend-Backend Communication**:
    -   Frontend Server Actions in `frontend/features/cv/actions.ts` call `cvService` (in `frontend/services/cv.service.ts`).
    -   `cvService` uses `apiClient` (Axios) to make requests to backend endpoints (`/cvs`, `/ai/cvs`).
-   **Background Tasks**: `asyncio.create_task` is used in `backend/app/modules/cv/service.py` to trigger AI analysis in the background.
