# DATN Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the DATN codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements to this job application platform.

### Document Scope

Comprehensive documentation of the entire system, focusing on the implemented authentication and user management features, with placeholders for planned CV processing, job matching, and contract analysis features.

### Change Log

| Date   | Version | Description                 | Author    |
| ------ | ------- | --------------------------- | --------- |
| 2025-12-09 | 1.0     | Initial brownfield analysis | AI Analyst |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Backend Main Entry**: `backend/app/main.py` (FastAPI app initialization)
- **Frontend Main Entry**: `frontend/app/layout.tsx` (Next.js root layout)
- **Database Config**: `backend/app/core/config.py` (PostgreSQL connection settings)
- **Auth Router**: `backend/app/modules/auth/router.py` (All authentication endpoints)
- **User Model**: `backend/app/modules/users/models.py` (User database schema)
- **Frontend Auth Actions**: `frontend/features/auth/actions.ts` (Server actions for auth)
- **API Client**: `frontend/services/api-client.ts` (Axios client with cookie support)

### Enhancement Impact Areas

[Planned features from user_story.md and tech.md]
- CV upload and OCR processing
- Interview practice rooms
- Job position suggestions via email
- Contract term checking

## High Level Architecture

### Technical Summary

DATN is a full-stack web application for job seekers, built with a modern Python backend and React frontend. The system currently implements user authentication and registration, with planned features for CV processing, job matching, and contract analysis.

### Actual Tech Stack

| Category  | Technology | Version | Notes                      |
| --------- | ---------- | ------- | -------------------------- |
| Backend Runtime   | Python | 3.x    | FastAPI framework |
| Backend Framework | FastAPI | >=0.104.1 | Async API framework |
| ORM | SQLAlchemy | >=2.0.23 | Database ORM |
| Database | PostgreSQL | - | Async driver: asyncpg |
| Migrations | Alembic | >=1.13.0 | Database schema migrations |
| Email | FastAPI-Mail | >=1.4.1 | Email sending |
| Auth | python-jose | >=3.3.0 | JWT tokens |
| Password Hashing | bcrypt | 4.0.1 | Via passlib |
| Validation | Pydantic | - | Data validation |
| Frontend Runtime | Node.js | - | Next.js framework |
| Frontend Framework | Next.js | 16.0.5 | React framework |
| UI Library | React | 19.2.0 | Component library |
| Styling | Tailwind CSS | ^4 | Utility-first CSS |
| Forms | React Hook Form | ^7.67.0 | Form handling |
| Validation | Zod | ^4.1.13 | Schema validation |
| HTTP Client | Axios | ^1.13.2 | API requests |

### Repository Structure Reality Check

- Type: Monorepo (backend/ and frontend/ directories)
- Package Managers: pip (backend), npm (frontend)
- Notable: Separate directories for backend and frontend, shared root for docs and config

## Source Tree and Module Organization

### Project Structure (Actual)

```
datn/
├── backend/
│   ├── alembic/                 # Database migrations
│   │   └── versions/            # Migration files
│   ├── app/
│   │   ├── api/v1/              # API version 1 router
│   │   ├── core/                # Core utilities (config, database, security, mailer)
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── modules/             # Business logic modules
│   │   │   ├── auth/            # Authentication module
│   │   │   ├── cvs/             # CV processing (empty)
│   │   │   ├── jobs/            # Job management (empty)
│   │   │   └── users/           # User management
│   │   └── templates/           # Email templates
│   ├── requirements.txt         # Python dependencies
│   └── alembic.ini              # Alembic config
├── frontend/
│   ├── app/                     # Next.js app directory
│   │   ├── (auth)/              # Auth pages (login, register, etc.)
│   │   ├── dashboard/           # Dashboard page
│   │   ├── globals.css          # Global styles
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   ├── components/              # Reusable components
│   │   ├── common/              # Common components (FormWrapper, PdfUploader)
│   │   └── ui/                  # UI components (button, input, card)
│   ├── features/                # Feature-specific code
│   │   └── auth/                # Auth feature (forms, actions, types)
│   ├── lib/                     # Utilities
│   ├── public/                  # Static assets
│   ├── services/                # API services
│   └── types/                   # TypeScript type definitions
├── .bmad-core/                  # BMAD methodology files
├── docs/                        # Documentation (planned)
├── .gitignore                   # Git ignore files
├── AGENTS.md                    # Agent configuration
├── GEMINI.md                    # Gemini config
├── opencode.jsonc               # OpenCode config
├── tech.md                      # Tech setup notes
├── user_story.md                # User stories
└── [other config files]
```

### Key Modules and Their Purpose

- **Auth Module** (`backend/app/modules/auth/`): Handles user authentication, registration, email verification, password reset
- **Users Module** (`backend/app/modules/users/`): User data management and database models
- **CVs Module** (`backend/app/modules/cvs/`): Planned CV upload and OCR processing (currently empty)
- **Jobs Module** (`backend/app/modules/jobs/`): Planned job posting and matching (currently empty)
- **Frontend Auth** (`frontend/features/auth/`): Authentication forms and server actions
- **API Client** (`frontend/services/api-client.ts`): HTTP client for backend communication

## Data Models and APIs

### Data Models

- **User Model**: See `backend/app/modules/users/models.py`
  - Fields: id, email, hashed_password, full_name, birthday, role, is_active, is_scraped, avatar, activation_code, etc.
  - Roles: admin, user, recruiter, student
  - Supports email activation and password reset workflows

### API Specifications

- **Base URL**: `/api/v1` (configured in settings)
- **Auth Endpoints**:
  - POST `/auth/register` - User registration with email activation
  - POST `/auth/verify-email` - Email verification
  - POST `/auth/login` - Login with JWT cookies
  - POST `/auth/refresh-token` - Refresh access token
  - POST `/auth/forgot-password` - Request password reset
  - POST `/auth/reset-password` - Reset password
  - POST `/auth/request-password-change` - Change password for logged-in users
  - POST `/auth/change-password` - Change password with OTP

## Technical Debt and Known Issues

### Critical Technical Debt

1. **Empty Business Modules**: CV and Jobs modules have empty model files, indicating incomplete implementation
2. **No Business Logic**: Core features (CV OCR, job matching, contract analysis) not implemented
3. **Database Schema**: Only users table exists; no tables for CVs, jobs, interviews, etc.
4. **Frontend Features**: Only authentication implemented; no CV upload, dashboard functionality
5. **Testing**: No test files visible in either backend or frontend
6. **Documentation**: Minimal documentation beyond basic setup notes

### Workarounds and Gotchas

- **CORS Configuration**: Frontend runs on port 3000, backend on 8000; CORS allows localhost origins
- **Cookie Authentication**: Uses HttpOnly cookies for JWT tokens; frontend relies on browser cookie handling
- **Email Templates**: Stored in `backend/app/templates/` directory
- **Environment Variables**: Requires .env file for database, email, and security settings

## Integration Points and External Dependencies

### External Services

| Service  | Purpose  | Integration Type | Key Files                      |
| -------- | -------- | ---------------- | ------------------------------ |
| PostgreSQL | Database | asyncpg driver | `backend/app/core/database.py` |
| Email SMTP | User notifications | FastAPI-Mail | `backend/app/core/mailer.py` |

### Internal Integration Points

- **Frontend-Backend**: REST API with cookie-based authentication
- **Database**: SQLAlchemy ORM with async operations
- **Email**: Template-based email sending for activation and password reset

## Development and Deployment

### Local Development Setup

1. Set up PostgreSQL database
2. Configure .env file with database credentials, email settings, JWT secret
3. Install backend dependencies: `pip install -r backend/requirements.txt`
4. Run database migrations: `alembic upgrade head`
5. Start backend: `uvicorn app.main:app --reload`
6. Install frontend dependencies: `npm install`
7. Start frontend: `npm run dev`

### Build and Deployment Process

- **Backend Build**: No build step required (Python)
- **Frontend Build**: `npm run build` (Next.js production build)
- **Deployment**: Not configured; manual deployment assumed

## Testing Reality

### Current Test Coverage

- Unit Tests: None visible
- Integration Tests: None visible
- E2E Tests: None visible
- Manual Testing: Primary testing method

### Running Tests

No test commands configured yet.

## Future Development Insights

### Planned Features

1. **CV Processing**:
   - PDF upload functionality
   - OCR text extraction
   - CV improvement suggestions

2. **Interview Practice**:
   - Virtual interview rooms
   - AI-powered feedback

3. **Job Matching**:
   - Job position scraping/suggestions
   - Email notifications to recruiters

4. **Contract Analysis**:
   - Employment contract review
   - Term validation

### Recommended Next Steps

1. Implement CV upload and storage
2. Add job posting models and APIs
3. Develop OCR integration for CV processing
4. Build interview practice features
5. Add comprehensive testing suite
6. Implement proper error handling and logging

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
npm run build
```

### Debugging and Troubleshooting

- **Backend Logs**: Check console output from uvicorn
- **Database**: Use pgAdmin or psql to inspect database
- **Frontend**: Check browser console and network tab
- **CORS Issues**: Ensure backend allows frontend origin
- **Cookie Issues**: Verify HttpOnly cookie settings in browser dev tools