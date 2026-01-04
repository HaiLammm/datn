# Backend - AI Recruitment Platform

This is the backend for the AI Recruitment Platform, built with FastAPI.

## Architecture

The backend follows a modular, feature-based architecture. Each feature (e.g., `auth`, `users`, `cv`) is a self-contained module with its own models, schemas, services, and routes. This is a simplified Domain-Driven Design approach.

### Directory Structure

```
backend/app/modules/
├── auth/
├── users/
├── cv/
└── jobs/
```

Each module contains:
*   `models.py`: SQLAlchemy models (database tables).
*   `schemas.py`: Pydantic models (data validation).
*   `service.py`: Business logic.
*   `router.py`: API endpoints.

## Tech Stack

*   **Framework:** FastAPI
*   **Database:** PostgreSQL with `asyncpg`, `sqlalchemy`, and `alembic` for migrations.
*   **Security:** `python-jose` for JWT, `passlib[bcrypt]` for password hashing.
*   **Validation:** Pydantic
*   **Configuration:** `pydantic-settings`

## Business Flows

*   **Authentication:** OAuth2 Password Flow with JWT Bearer Tokens. Passwords are hashed with `passlib`.
    *   **Registration:** Includes an email verification step with OTP.
    *   **Login:** Compares user-provided password with the hashed password in the database.
*   **Password Management:** Secure password change and reset flows using OTP.

## API Endpoints

The API is versioned under `/api/v1`.

### Auth (`/auth`)
*   `POST /register`: Register a new user.
*   `POST /verify-email`: Verify user's email with OTP.
*   `POST /login`: Log in and get an access token.
*   `POST /request-password-change`: Request a password change (for logged-in users).
*   `POST /change-password`: Change password with OTP (for logged-in users).
*   `POST /forgot-password`: Request a password reset (for logged-out users).
*   `POST /reset-password`: Reset password with OTP.

### Users (`/users`)
*   `GET /me`: Get the current user's details.

(CV and Job modules are planned but not yet implemented).
