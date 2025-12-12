# Development and Deployment

## Local Development Setup

-   **Backend**: Requires Python environment, `pip install -r requirements.txt`, PostgreSQL database, and Ollama running.
-   **Frontend**: Requires Node.js, `npm install`, and `npm run dev`.
-   Environment variables need to be configured in a `.env` file for the backend.

## Build and Deployment Process

-   **Backend**: No specific build step, runs directly with Uvicorn.
-   **Frontend**: `npm run build` for Next.js production build.
-   Currently, deployment is manual.
