# Appendix - Useful Commands and Scripts

## Frequently Used Commands

-   **Backend Development**: `uvicorn app.main:app --reload` (from `backend/app/` directory).
-   **Frontend Development**: `npm run dev` (from `frontend/` directory).
-   **Database Migrations**: `alembic revision --autogenerate -m "description"`, `alembic upgrade head` (from `backend/` directory).
-   **Running Tests**: `pytest` (from `backend/` directory), `npm test` (from `frontend/` directory).
-   **Ollama**: `ollama run llama3.1:8b` (to ensure the model is downloaded and running).