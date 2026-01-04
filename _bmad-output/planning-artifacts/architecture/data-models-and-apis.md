# Data Models and APIs

## Data Models

-   **User Model**: Defined in `backend/app/modules/users/models.py`.
-   **CV Model**: Defined in `backend/app/modules/cv/models.py`. Table name is `cvs`. Linked to `users` via `user_id`.
-   **CVAnalysis Model**: Defined in `backend/app/modules/ai/models.py`. Linked to `cvs` via `cv_id`.
-   Other relevant models (e.g., Job) are yet to be implemented.

## API Specifications

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
