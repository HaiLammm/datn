# AI Recruitment Platform

This is a full-stack AI-powered recruitment platform.

## Overview

The project consists of two main parts:

*   **Frontend:** A Next.js application (port 3000)
*   **Backend:** A FastAPI (Python) application (port 8000)

The system is designed to provide intelligent features like AI matching and CV parsing.

## Communication Protocol

*   **API Base URL (Dev):** `http://localhost:8000/api/v1`
*   **Format:** JSON for requests and responses.
*   **Authentication:** The system uses HttpOnly cookies for authentication. The frontend automatically sends credentials with each request.
*   **CORS:** The backend is configured to accept requests from `http://localhost:3000`.

## Backend

The backend is a FastAPI application responsible for business logic, data processing, and serving the API.

Key features:
*   Modular, feature-based architecture.
*   Uses SQLAlchemy for database interaction and Alembic for migrations.
*   Handles user authentication with JWT and password hashing.
*   Provides APIs for user management, CV processing, and job postings.

For more details, see the `backend/README.md`.

## Frontend

The frontend is a Next.js application using the App Router.

Key features:
*   "Feature-first" architecture, with code organized by business logic modules.
*   Uses `shadcn/ui` for UI components and Tailwind CSS for styling.
*   Uses Server Actions for communication with the backend.
*   Follows a strict "Server Component"-first strategy.

For more details, see the `frontend/README.md`.
