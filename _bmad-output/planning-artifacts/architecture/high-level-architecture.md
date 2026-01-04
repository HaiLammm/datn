# High Level Architecture

## Technical Summary

The DATN project is a full-stack web application following a Client-Server Model. The Backend is built with FastAPI (Python) and PostgreSQL, running on port 8000. The Frontend is a Next.js (React) application, utilizing the App Router, Shadcn/ui, and Tailwind CSS, running on port 3000. Authentication is cookie-based (HttpOnly Cookies). The current enhancement focuses on integrating AI-powered CV analysis via Ollama, adding CV management, and laying groundwork for job matching.

## Actual Tech Stack

| Category         | Technology               | Version      | Notes                                                                                                                  |
| :--------------- | :----------------------- | :----------- | :----------                                                                                                          |
| **Backend**      |                          |              |                                                                                                                        |
| Runtime          | Python                   | 3.x          |                                                                                                                        |
| Framework        | FastAPI                  | >=0.104.1    | High-performance web framework.                                                                                        |
| ASGI Server      | Uvicorn                  | >=0.24.0     |                                                                                                                        |
| ORM              | SQLAlchemy               | >=2.0.23     | Used for database interactions.                                                                                        |
| DB Driver        | Asyncpg                  | >=0.29.0     | Asynchronous PostgreSQL driver.                                                                                        |
| Migrations       | Alembic                  | >=1.13.0     | Database migration tool.                                                                                               |
| Auth             | python-jose, passlib     | >=3.3.0,     | JWT generation/validation, bcrypt password hashing.                                                                    |
| Config/Validation| Pydantic, pydantic-settings | >=2.5.2,     | Data validation and environment variable management.                                                                   |
| AI Integration   | httpx                    | >=0.25.0     | Asynchronous HTTP client for Ollama API calls.                                                                         |
| Text Extraction  | PyMuPDF (fitz)           | >=1.23.0     | PDF text extraction.                                                                                                   |
| Text Extraction  | python-docx              | >=1.1.0      | DOCX text extraction.                                                                                                  |
| Email            | fastapi-mail             | >=1.4.1      | Asynchronous email sending.                                                                                            |
| **Frontend**     |                          |              |                                                                                                                        |
| Runtime          | Node.js                  |              |                                                                                                                        |
| Framework        | Next.js                  | 16.0.5       | App Router, Server Components/Actions strategy.                                                                        |
| UI Library       | Shadcn/ui, Tailwind CSS  | ^4           | Component library and styling framework.                                                                               |
| Icons            | Lucide React             |              | Icon library.                                                                                                          |
| Forms            | react-hook-form, Zod     | ^7.67.0,     | Form management and client-side validation.                                                                            |
| HTTP Client      | Axios                    | ^1.13.2      | Configured via `api-client.ts`.                                                                                        |

## Repository Structure Reality Check

-   Type: Monorepo (Backend and Frontend are separate projects within the same repository)
-   Package Manager: `npm` (Frontend), `pip` (Backend)
-   Notable: Shared types are defined in `packages/shared-types/`.
