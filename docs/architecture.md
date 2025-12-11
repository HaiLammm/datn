# AI Recruitment Platform Fullstack Architecture Document

## Introduction

This document outlines the complete fullstack architecture for the AI Recruitment Platform, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### Starter Template or Existing Project

The project is built upon an existing full-stack web application with a Python/FastAPI backend and a Next.js/React frontend. The current project state focuses exclusively on a complete and secure user authentication and registration system. Core business features for CV analysis and job matching are planned as a major enhancement.

### Change Log

| Date | Version | Description | Author |
| :---------- | :---------- | :---------- | :---------- |
| 2025-12-10 | 0.1.0 | Initial draft of the Fullstack Architecture Document. | Winston (Architect) |

---
## High Level Architecture

### Technical Summary

The architecture is a modern full-stack application composed of a Next.js frontend and a Python (FastAPI) backend, designed for modularity and scalability. The frontend will be deployed on Vercel to leverage its powerful CDN and CI/CD capabilities. The backend, along with the PostgreSQL database and the Ollama AI service, will be self-hosted on a dedicated Linux server to comply with the critical requirement of local, private AI data processing. Integration between the frontend and backend is achieved via a RESTful API, secured with an HttpOnly cookie-based authentication flow. This architecture directly supports the PRD goals by providing a high-performance user experience, ensuring data privacy for sensitive CV and JD information, and creating a scalable foundation for future AI-driven features.

### Platform and Infrastructure Choice

Based on the PRD's requirement for local AI processing (NFR5) and the need for a high-performance frontend, a hybrid platform approach is recommended.

**Platform:** **Vercel (Frontend)** + **Self-Hosted Server (Backend & AI)**
**Key Services:**
*   **Vercel:** Next.js Hosting, Global CDN, CI/CD (for Frontend).
*   **Self-Hosted Server (Linux - Ubuntu 22.04 LTS):**
    *   **FastAPI Backend Hosting:** Running the Python application via Uvicorn.
    *   **PostgreSQL:** Relational database for application data.
    *   **Ollama:** Serving local Large Language Models for all AI tasks.
    *   **NGINX:** As a reverse proxy for the FastAPI application.
**Deployment Host and Regions:**
*   **Vercel:** Deployed to Vercel's global edge network.
*   **Self-Hosted Server:** A single server instance will be provisioned in a secure data center (e.g., AWS EC2, DigitalOcean, or on-premise). The specific region should be chosen to minimize latency for the primary user base.

### Repository Structure

The project will use a **Monorepo** structure to manage the `frontend` and `backend` applications within a single Git repository. This approach simplifies dependency management and facilitates code sharing.

**Structure:** Monorepo
**Monorepo Tool:** **npm Workspaces** (Leveraging built-in npm capabilities is sufficient for the current scale and avoids adding extra dependencies).
**Package Organization:**
*   `apps/frontend`: The Next.js application.
*   `apps/backend`: The FastAPI application.
*   `packages/shared-types`: A new shared package for TypeScript interfaces and Zod schemas used by both frontend and backend to ensure type safety across the stack.

### High Level Architecture Diagram

```mermaid
graph TD
    subgraph "User's Browser"
        A[User] --> B{Next.js Frontend};
    end

    subgraph "Vercel Platform"
        B -- HTTPS --> C[Vercel Edge Network / CDN];
    end

    subgraph "Self-Hosted Linux Server (e.g., AWS EC2)"
        C -- API Calls --> D[NGINX Reverse Proxy];
        D --> E[FastAPI Backend];
        E -- CRUD Ops --> F[PostgreSQL Database];
        E -- AI Tasks (Async) --> G[Ollama LLM Service];
    end

    style G fill:#f9f,stroke:#333,stroke-width:2px
```

### Architectural Patterns

- **Modular Monolith (Backend):** The FastAPI backend is organized into feature-based modules (e.g., `auth`, `users`, `cvs`). This provides clear separation of concerns while maintaining the simplicity of a single deployment unit.
- **Jamstack (Frontend):** The Next.js application leverages static site generation (SSG) for shell pages and client-side rendering (CSR) for dynamic, user-specific data, ensuring optimal performance and SEO.
- **Server Actions (Frontend):** For mutations and data fetching from the client, Next.js Server Actions will be used. This co-locates data operations with the components that use them, simplifying client-side state management.
- **Asynchronous Task Processing (Backend):** For long-running AI operations like CV parsing, FastAPI's `BackgroundTasks` will be used to immediately return a response to the user while processing the task in the background, as required by NFR2.
- **Repository Pattern (Backend):** The use of a `service.py` layer in each module abstracts business logic from the API endpoints (`router.py`) and data access, improving testability and maintainability.

---
### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | | | | |
| Frontend Language | TypeScript | `~5` | Language for frontend development. | Provides static typing to reduce runtime errors and improve developer experience. |
| Frontend Framework | Next.js / React | `16.0.5` / `19.2.0` | UI framework for building the user interface. | Enables server-side rendering, static site generation, and a powerful component model. |
| UI Component Library | shadcn/ui | latest | Building blocks for the user interface. | A set of reusable, accessible, and themeable components built on Radix UI and Tailwind CSS. |
| State Management | React Context / Hooks | `19.2.0` | Managing application state. | Sufficient for current needs; avoids adding extra libraries for simple state. `react-hook-form` is used for forms. |
| CSS Framework | Tailwind CSS | `^4` | Styling the application. | A utility-first CSS framework for rapid UI development and easy customization. |
| **Backend** | | | | |
| Backend Language | Python | `~3.11` | Language for backend development. | A robust, widely-used language with a strong ecosystem for web development and data science. |
| Backend Framework | FastAPI | `>=0.104.1` | Web framework for building APIs. | High-performance, easy-to-use framework with automatic docs and async support. |
| API Style | REST | `N/A` | Defines how the frontend and backend communicate. | A mature, well-understood standard for building web APIs. |
| **Data & Storage**| | | | |
| Database | PostgreSQL | `15+` | Primary data store for user and application data. | A powerful, open-source object-relational database system with a strong reputation for reliability. |
| Cache | Redis | `7.x` | In-memory data store for caching and session management. | *Proposed for future use.* Provides high-performance caching to reduce database load. |
| File Storage | Local Filesystem | `N/A` | Storing uploaded user files (e.g., CVs). | Meets the requirement for local data processing and avoids external service dependencies. |
| **Security** | | | | |
| Authentication | JWT (python-jose) & Passlib | `>=3.3.0` | Securely authenticating users and managing sessions. | Standard secure combination for token-based auth and password hashing in Python. |
| **Testing** | | | | |
| Frontend Testing | Jest & React Testing Library | `latest` | Unit and integration testing for frontend components. | *Proposed.* Industry standard for testing React applications. |
| Backend Testing | Pytest & HTTPX | `latest` | Unit and integration testing for the FastAPI backend. | *Proposed.* Pytest is the standard Python testing framework; HTTPX for testing async APIs. |
| E2E Testing | Playwright | `latest` | End-to-end testing of user flows. | *Proposed.* A modern, reliable framework for testing across different browsers. |
| **DevOps** | | | | |
| Build Tool | npm | `latest` | Managing frontend dependencies and running scripts. | The default package manager for the Node.js ecosystem. |
| Bundler | Next.js internal (Webpack) | `N/A` | Bundling JavaScript code for the browser. | Handled automatically by Next.js, providing an optimized build process out-of-the-box. |
| IaC Tool | Docker Compose | `latest` | Defining and running the local multi-service application. | *Proposed.* Simplifies local development setup for the backend, DB, and AI service. |
| CI/CD | Vercel & GitHub Actions | `N/A` | Automating builds, tests, and deployments. | Vercel provides seamless CI/CD for the frontend. GitHub Actions will be used for backend linting and testing. |
| **Operations** | | | | |
| Monitoring | Vercel Analytics & Prometheus | `N/A` | Monitoring application performance and health. | *Proposed.* Vercel for frontend insights; Prometheus/Grafana for backend/infra monitoring. |
| Logging | Vercel Logs & Python Logging | `N/A` | Recording application events and errors. | Vercel captures frontend/serverless logs. Python's built-in logging is sufficient for the backend. |

---
## Data Models

### **Updated `CV` Model (Hybrid Approach)**

**Purpose:** To store uploaded CVs, their full parsed content, and key indexed fields for efficient searching.

**Key Attributes:**
- `id`: UUID
- `user_id`: UUID
- `filename`: String
- `file_path`: String
- `uploaded_at`: DateTime
- `parsed_content`: **JSONB** - _(Contains the full, raw AI extraction for flexibility)._
- `summary`: Text
- `quality_score`: Integer
- `ats_compatibility_feedback`: Text
- `is_active`: Boolean
- `extracted_skills`: **Array of Text** - _(NEW - Indexed for fast skill-based searches)._
- `total_experience_years`: **Integer** - _(NEW - Indexed for filtering by experience level)._

#### TypeScript Interface
```typescript
interface CV {
  id: string;
  userId: string;
  filename: string;
  filePath: string;
  uploadedAt: string;
  parsedContent: Record<string, any>;
  summary: string;
  qualityScore: number;
  atsCompatibilityFeedback: string;
  isActive: boolean;
  extractedSkills: string[]; // NEW
  totalExperienceYears: number; // NEW
}
```

---

### **Updated `JobDescription` Model (Structured Approach)**

**Purpose:** To store job descriptions with both full-text for semantic search and structured fields for precise filtering.

**Key Attributes:**
- `id`: UUID
- `user_id`: UUID
- `title`: String
- `description`: Text - _(Full original text for semantic matching)._
- `uploaded_at`: DateTime
- `is_active`: Boolean
- `required_skills`: **Array of Text** - _(NEW - For skill-based matching and filtering)._
- `min_experience_years`: **Integer** - _(NEW - For filtering by minimum experience)._
- `location_type`: **String** (`'remote' | 'hybrid' | 'on-site'`) - _(NEW - For location-based filtering)._
- `salary_min`: **Integer** - _(NEW - For salary range filtering)._
- `salary_max`: **Integer** - _(NEW - For salary range filtering)._

#### TypeScript Interface
```typescript
type LocationType = 'remote' | 'hybrid' | 'on-site';

interface JobDescription {
  id: string;
  userId: string;
  title: string;
  description: string;
  uploadedAt: string;
  isActive: boolean;
  requiredSkills: string[]; // NEW
  minExperienceYears: number; // NEW
  locationType: LocationType; // NEW
  salaryMin?: number; // NEW - Optional
  salaryMax?: number; // NEW - Optional
}
```

---
## API Specification

### REST API Specification

```yaml
openapi: 3.0.0
info:
  title: AI Recruitment Platform API
  version: 1.0.0
  description: API for AI-powered CV analysis, job matching, and user management.
servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.ai-recruitment.com/api/v1 # Placeholder for production
    description: Production server
security:
  - CookieAuth: []
components:
  securitySchemes:
    CookieAuth:
      type: apiKey
      in: cookie
      name: access_token # The name of the cookie FastAPI sets
  schemas:
    ErrorResponse:
      type: object
      properties:
        detail:
          type: string
          description: Detailed error message
      example:
        detail: "Tài khoản không tồn tại hoặc mật khẩu không đúng."

    # Existing Auth Schemas
    UserLoginInput:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
    UserRegisterInput:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
    VerifyEmailInput:
      type: object
      required:
        - email
        - activation_code
      properties:
        email:
          type: string
          format: email
        activation_code:
          type: string
    User: # Placeholder for User profile schema
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        is_active:
          type: boolean
        # ... other user fields

    # New CV Schemas
    CVUploadInput:
      type: object
      required:
        - file
      properties:
        file:
          type: string
          format: binary # For file upload
    CV: # Schema for CV response
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        filename:
          type: string
        uploaded_at:
          type: string
          format: date-time
        parsed_content:
          type: object
        summary:
          type: string
        quality_score:
          type: integer
        ats_compatibility_feedback:
          type: string
        is_active:
          type: boolean
        extracted_skills:
          type: array
          items:
            type: string
        total_experience_years:
          type: integer
    CVList:
      type: array
      items:
        $ref: '#/components/schemas/CV'

    # New JobDescription Schemas
    JDUploadInput:
      type: object
      required:
        - title
        - description
        - file # Optional: for uploading JD document
      properties:
        file:
          type: string
          format: binary # For file upload
        title:
          type: string
        description:
          type: string
        required_skills:
          type: array
          items:
            type: string
        min_experience_years:
          type: integer
        location_type:
          type: string
          enum: [ "remote", "hybrid", "on-site" ]
        salary_min:
          type: integer
        salary_max:
          type: integer
    JobDescription:
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        title:
          type: string
        description:
          type: string
        uploaded_at:
          type: string
          format: date-time
        is_active:
          type: boolean
        required_skills:
          type: array
          items:
            type: string
        min_experience_years:
          type: integer
        location_type:
          type: string
          enum: [ "remote", "hybrid", "on-site" ]
        salary_min:
          type: integer
        salary_max:
          type: integer

    CandidateMatchResult: # Placeholder for candidate matching results
      type: object
      properties:
        candidate_id:
          type: string
          format: uuid
        cv_id:
          type: string
          format: uuid
        match_score:
          type: number
          format: float
        reasons:
          type: array
          items:
            type: string

paths:
  /auth/register:
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRegisterInput'
      responses:
        '200':
          description: User successfully registered, activation email sent
        '400':
          description: Invalid input or user already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/verify-email:
    post:
      summary: Verify user email with activation code
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VerifyEmailInput'
      responses:
        '200':
          description: Email successfully verified
        '400':
          description: Invalid email or activation code
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/login:
    post:
      summary: Authenticate user and receive access tokens
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserLoginInput'
      responses:
        '200':
          description: User logged in, HttpOnly cookies set for access_token and refresh_token
          headers:
            Set-Cookie:
              schema:
                type: string
                example: "access_token=your-token; HttpOnly; Path=/; SameSite=Lax; refresh_token=your-refresh-token; HttpOnly; Path=/; SameSite=Lax;"
        '400':
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/request-password-change:
    post:
      summary: Request a password change (sends OTP) - Authenticated
      # ... other request/response schemas
      responses:
        '200':
          description: OTP sent to user email
        '401':
          description: Unauthorized
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/change-password:
    post:
      summary: Change password using OTP - Authenticated
      # ... other request/response schemas
      responses:
        '200':
          description: Password successfully changed
        '401':
          description: Unauthorized
        '400':
          description: Invalid OTP or password
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/forgot-password:
    post:
      summary: Request password reset (sends OTP) - Unauthenticated
      # ... other request/response schemas
      responses:
        '200':
          description: OTP sent to user email
        '400':
          description: Invalid email
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/reset-password:
    post:
      summary: Reset password using OTP - Unauthenticated
      # ... other request/response schemas
      responses:
        '200':
          description: Password successfully reset
        '400':
          description: Invalid OTP or password
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /users/me:
    get:
      summary: Get current authenticated user's profile
      security:
        - CookieAuth: []
      responses:
        '200':
          description: Current user's profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /cvs:
    post:
      summary: Upload a new CV for analysis
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data: # For file upload
            schema:
              $ref: '#/components/schemas/CVUploadInput'
      responses:
        '201':
          description: CV uploaded and analysis initiated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CV'
        '400':
          description: Invalid file format or request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized
    get:
      summary: Get all CVs uploaded by the current user
      security:
        - CookieAuth: []
      responses:
        '200':
          description: List of user's CVs
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CVList'
        '401':
          description: Unauthorized

  /cvs/{cv_id}:
    get:
      summary: Get details of a specific CV by ID
      security:
        - CookieAuth: []
      parameters:
        - name: cv_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: CV details and analysis
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CV'
        '401':
          description: Unauthorized
        '404':
          description: CV not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    delete:
      summary: Delete a specific CV by ID
      security:
        - CookieAuth: []
      parameters:
        - name: cv_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: CV successfully deleted
        '401':
          description: Unauthorized
        '404':
          description: CV not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /jobs/jd:
    post:
      summary: Upload a new Job Description
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data: # For file upload or structured data
            schema:
              $ref: '#/components/schemas/JDUploadInput'
      responses:
        '201':
          description: Job Description uploaded and processed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobDescription'
        '400':
          description: Invalid input or request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized

  /jobs/jd/{jd_id}/candidates:
    get:
      summary: Get ranked candidates for a specific Job Description
      security:
        - CookieAuth: []
      parameters:
        - name: jd_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: List of ranked candidates
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CandidateMatchResult'
        '401':
          description: Unauthorized
        '404':
          description: Job Description not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /jobs/search:
    post:
      summary: Semantic search for candidates based on query
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - query
              properties:
                query:
                  type: string
                  description: Natural language search query for candidates
      responses:
        '200':
          description: List of candidates matching the query
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CandidateMatchResult'
        '401':
          description: Unauthorized
        '400':
          description: Invalid search query
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
```

---
## Components

### Component List

#### Backend Components

**Auth Service**
-   **Responsibility:** Handles user registration, login/logout, password management, and JWT/cookie generation.
-   **Key Interfaces:** Provides `/api/v1/auth/*` endpoints.
-   **Dependencies:** `User Service`, `Database Service`.
-   **Technology Stack:** FastAPI, Passlib, python-jose, SQLAlchemy.

**User Service**
-   **Responsibility:** Manages user profile data and state.
-   **Key Interfaces:** Provides `/api/v1/users/me` endpoint.
-   **Dependencies:** `Database Service`.
-   **Technology Stack:** FastAPI, SQLAlchemy.

**CV Processing Service**
-   **Responsibility:** Manages CV uploads, storage, and orchestrates the AI analysis pipeline (parsing, scoring, feedback).
-   **Key Interfaces:** Provides `/api/v1/cvs/*` endpoints.
-   **Dependencies:** `AI Service`, `Database Service`, `File Storage`.
-   **Technology Stack:** FastAPI, SQLAlchemy, BackgroundTasks.

**Job & Matching Service**
-   **Responsibility:** Manages Job Description uploads and orchestrates the AI-powered candidate matching and semantic search.
-   **Key Interfaces:** Provides `/api/v1/jobs/*` endpoints.
-   **Dependencies:** `AI Service`, `Database Service`.
-   **Technology Stack:** FastAPI, SQLAlchemy.

**AI Service (Ollama Wrapper)**
-   **Responsibility:** A dedicated internal service that acts as a wrapper around the Ollama LLM. It abstracts the raw AI calls into specific business functions like `parse_cv(file_content)` or `rank_candidates(jd_text, cv_texts)`.
-   **Key Interfaces:** Internal Python functions (not a public API).
-   **Dependencies:** Ollama LLM service endpoint.
-   **Technology Stack:** Python (`httpx` or `aiohttp` for async calls to Ollama).

#### Frontend Components

**API Service Layer (`/services`)**
-   **Responsibility:** Encapsulates all communication with the backend REST API. It abstracts away `fetch`/`axios` calls and standardizes error handling and authentication header/cookie management. This is where we will handle the cookie forwarding for SSR as noted.
-   **Key Interfaces:** Provides async functions (e.g., `authService.login()`, `cvService.uploadCV()`).
-   **Dependencies:** Next.js Server Actions, `axios`.
-   **Technology Stack:** TypeScript, Axios.

**Feature Components (`/features`)**
-   **Responsibility:** Self-contained UI and logic for major business features (e.g., `LoginForm`, `CVUploadForm`). They handle user interaction and orchestrate calls to the API Service Layer.
-   **Key Interfaces:** React components consumed by the main application pages.
-   **Dependencies:** `API Service Layer`, `UI Component Library`, `State Management`.
-   **Technology Stack:** React, Next.js, `react-hook-form`.

**UI Component Library (`/components/ui`)**
-   **Responsibility:** Provides the set of generic, reusable, and style-compliant UI primitives based on `shadcn/ui`.
-   **Key Interfaces:** React component props (e.g., `<Button>`, `<Input>`).
-   **Dependencies:** React, Tailwind CSS.
-   **Technology Stack:** React, Radix UI, `class-variance-authority`.

**State Management**
-   **Responsibility:** Manages client-side state, both local (component state) and global (user session).
-   **Key Interfaces:** React Hooks (`useState`, `useContext`) and `useActionState` for form interactions.
-   **Dependencies:** React.
-   **Technology Stack:** React Hooks, React Context API.

### Component Diagrams

Here is a C4-style Container diagram showing the high-level relationships between these logical components.

```mermaid
graph TD
    subgraph "Browser"
        User -- "Interacts" --> FE_Features["Frontend: Feature Components"]
    end

    subgraph "Next.js Frontend (Vercel)"
        FE_Features -- "Uses" --> FE_State["Frontend: State Management"]
        FE_Features -- "Calls" --> FE_API_Service["Frontend: API Service Layer"]
        FE_Features -- "Renders" --> FE_UI["Frontend: UI Library"]
    end

    subgraph "FastAPI Backend (Self-Hosted)"
        FE_API_Service -- "HTTPS/API Calls" --> BE_Auth["Backend: Auth Service"]
        FE_API_Service -- "HTTPS/API Calls" --> BE_User["Backend: User Service"]
        FE_API_Service -- "HTTPS/API Calls" --> BE_CV["Backend: CV Service"]
        FE_API_Service -- "HTTPS/API Calls" --> BE_Jobs["Backend: Job & Matching Service"]

        BE_Auth --> BE_DB[("Database Service<br/>(PostgreSQL)")];
        BE_User --> BE_DB;
        BE_CV --> BE_DB;
        BE_Jobs --> BE_DB;

        BE_CV -- "Processes" --> BE_Storage[("File Storage<br/>(Local Filesystem)")];

        BE_CV -- "Async Tasks" --> BE_AI;
        BE_Jobs -- "Async Tasks" --> BE_AI;

        subgraph "Internal AI Abstraction"
            BE_AI["Backend: AI Service"] -- "HTTP" --> Ollama[("Ollama LLM")];
        end
    end

    style Ollama fill:#f9f,stroke:#333,stroke-width:2px
```

---
## External APIs

### Email Sending Service (SMTP Provider)

-   **Purpose:** To reliably send transactional emails to users for account activation, password reset requests, and other system notifications.
-   **Documentation:** Varies by provider (e.g., SendGrid, Mailgun, AWS SES, Gmail SMTP). Typically involves standard SMTP protocol documentation.
-   **Base URL(s):** Provider-specific SMTP server address (e.g., `smtp.sendgrid.net`, `smtp.mailgun.org`, `email-smtp.us-east-1.amazonaws.com`).
-   **Authentication:** Typically requires a username (often an API key or dedicated SMTP username) and a password (or API key). Authentication is performed over TLS.
-   **Rate Limits:** Provider-specific. Free tiers usually have daily sending limits (e.g., 100-10,000 emails/day), which scale with paid plans.
-   **Key Endpoints Used:** Standard SMTP commands (`HELO`, `AUTH`, `MAIL FROM`, `RCPT TO`, `DATA`, `QUIT`).
-   **Integration Notes:**
    *   The `fastapi-mail` library handles the SMTP communication.
    *   Credentials will be stored securely as environment variables.

---
## Core Workflows

### Job Seeker Uploads CV for Analysis

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Frontend_Client as Frontend (Client)
    participant Frontend_SSR as Frontend (SSR/Server Action)
    participant API_Gateway as API Gateway/FastAPI
    participant DB as PostgreSQL DB
    participant AIS as AI Service (Wrapper)
    participant Ollama as Ollama LLM

    User->>Browser: Selects CV file and clicks "Upload"
    Browser->>Frontend_Client: Triggers form submission (e.g., via useActionState)
    Frontend_Client->>Frontend_SSR: Submits form data (including file) to Server Action
    Frontend_SSR->>Frontend_SSR: Validates input (Zod)
    Frontend_SSR->>API_Gateway: POST /api/v1/cvs (multipart/form-data, with cookies)
    activate API_Gateway
    API_Gateway->>DB: Store temporary CV file metadata (status: PENDING)
    activate DB
    DB-->>API_Gateway: CV ID returned
    deactivate DB
    API_Gateway->>API_Gateway: Initiates AI processing in background task (FastAPI BackgroundTasks)
    API_Gateway-->>Frontend_SSR: 201 Created (CV ID, status: PENDING)
    deactivate API_Gateway
    Frontend_SSR->>Frontend_Client: Returns result (CV ID, status)
    Frontend_Client->>Browser: Displays "CV Uploaded, Analysis Pending..." message

    Note over API_Gateway,Ollama: Asynchronous AI Processing

    API_Gateway->>AIS: Calls process_cv(cv_id, file_path)
    activate AIS
    AIS->>Ollama: Sends CV content for parsing/analysis
    activate Ollama
    Ollama-->>AIS: Returns parsed content, score, feedback
    deactivate Ollama
    AIS-->>API_Gateway: Returns AI results
    deactivate AIS
    API_Gateway->>DB: Updates CV record with parsed content, score, feedback (status: COMPLETED)
    activate DB
    DB-->>API_Gateway: Update successful
    deactivate DB

    Note over API_Gateway,Browser: User periodically checks status or receives notification

    Frontend_Client->>API_Gateway: GET /api/v1/cvs/{cv_id} (or refresh list)
    activate API_Gateway
    API_Gateway->>DB: Retrieve CV details
    activate DB
    DB-->>API_Gateway: CV details (status: COMPLETED)
    deactivate DB
    API_Gateway-->>Frontend_Client: Returns CV details (parsed content, score, etc.)
    deactivate API_Gateway
    Frontend_Client->>Browser: Displays CV analysis results
```

---
## Database Schema

### **Revised `Database Schema` (Updated with Vector Dimension 768)**

```sql
-- Assumes the 'pgvector' extension is installed: CREATE EXTENSION IF NOT EXISTS vector;

-- Existing 'users' table (simplified for context)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------------------------------

-- New 'cvs' table
CREATE TABLE IF NOT EXISTS cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_content JSONB,
    summary TEXT,
    quality_score INTEGER,
    ats_compatibility_feedback TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Indexed fields for filtering
    extracted_skills TEXT[],
    total_experience_years INTEGER,

    -- NEW: Vector embedding for semantic search, dimension 768 as specified
    embedding VECTOR(768),

    -- Foreign key constraint with ON DELETE CASCADE
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cvs_user_id ON cvs (user_id);
CREATE INDEX IF NOT EXISTS idx_cvs_extracted_skills ON cvs USING GIN (extracted_skills);
CREATE INDEX IF NOT EXISTS idx_cvs_total_experience_years ON cvs (total_experience_years);
-- NEW: Index for vector similarity search (e.g., IVFFlat)
CREATE INDEX IF NOT EXISTS idx_cvs_embedding ON cvs USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

--------------------------------------------------------------------------------

-- New 'job_descriptions' table
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Structured fields for filtering
    required_skills TEXT[],
    min_experience_years INTEGER,
    location_type VARCHAR(50) NOT NULL CHECK (location_type IN ('remote', 'hybrid', 'on-site')),
    salary_min INTEGER,
    salary_max INTEGER,

    -- NEW: Vector embedding for semantic search, dimension 768 as specified
    embedding VECTOR(768),

    -- Foreign key constraint with ON DELETE CASCADE
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_required_skills ON job_descriptions USING GIN (required_skills);
-- ... other indexes from before ...
-- NEW: Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_job_descriptions_embedding ON job_descriptions USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

---
## Frontend Architecture

### Component Architecture

#### Component Organization

The frontend code is organized using a **Feature-First (Vertical Slice) Architecture**. This means code is grouped by business domain rather than by type of file.

```plaintext
frontend/
├── app/                  # Next.js App Router (page.tsx, layout.tsx, etc.)
│   ├── (auth)/           # Grouping for authentication-related routes
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   └── layout.tsx
└── features/             # Business Logic Modules
    ├── auth/             # Authentication feature
    │   ├── components/   # Feature-specific UI (LoginForm.tsx, RegisterForm.tsx)
    │   ├── hooks/        # Feature-specific logic (e.g., useAuth)
    │   ├── types.ts      # Local Interfaces & Zod Schemas
    │   └── actions.ts    # Server Actions for auth
    ├── cv/               # CV management feature
    │   ├── components/   # CVUploadForm.tsx, CVList.tsx
    │   └── actions.ts    # Server Actions for CVs
    └── jobs/             # Job/JD management feature
        ├── components/   # JDUploadForm.tsx, JobMatchResults.tsx
        └── actions.ts    # Server Actions for Jobs
```

#### Component Template

A standard React functional component template for feature-specific UI components will utilize TypeScript, merge Tailwind CSS classes using `cn()`, and clearly define props.

```typescript
// features/auth/components/LoginForm.tsx
'use client'; // This is a Client Component

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useActionState } from "react";
import { loginAction } from "../actions"; // Assuming an actions.ts file

interface LoginFormProps extends React.ComponentPropsWithoutRef<'form'> {
  // Add specific props for the login form if needed
}

export function LoginForm({ className, ...props }: LoginFormProps) {
  const [state, formAction] = useActionState(loginAction, undefined);

  return (
    <form action={formAction} className={cn("grid gap-4", className)} {...props}>
      <div className="grid gap-2">
        <label htmlFor="email">Email</label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="m@example.com"
          required
        />
        {state?.errors?.email && (
          <p className="text-red-500 text-sm">{state.errors.email}</p>
        )}
      </div>
      <div className="grid gap-2">
        <label htmlFor="password">Password</label>
        <Input
          id="password"
          name="password"
          type="password"
          required
        />
        {state?.errors?.password && (
          <p className="text-red-500 text-sm">{state.errors.password}</p>
        )}
      </div>
      <Button type="submit" className="w-full">
        Login
      </Button>
      {state?.message && (
        <p className="text-red-500 text-sm">{state.message}</p>
      )}
    </form>
  );
}
```

### State Management Architecture

#### State Structure

Frontend state management adheres to a layered approach:

-   **Local Component State:** Managed using React's `useState` and `useReducer` hooks for UI-specific data (e.g., form input values, loading indicators within a component).
-   **Form State & Validation:** Handled comprehensively by `react-hook-form` in conjunction with `Zod` for schema validation. This provides robust and efficient form management.
-   **Server Action State:** For forms that submit data via Next.js Server Actions, `useActionState` (React 19) is used. This hook manages the state of the last form submission and any errors, directly integrating with the Server Action's return value.
-   **Global Application State:** For application-wide data (e.g., current authenticated user details, theme settings), React's Context API will be used. This provides a simple and effective way to share state without prop-drilling.

#### State Management Patterns

-   `useState` & `useReducer`: For isolated, component-level state.
-   `useContext`: For global, application-wide data that needs to be accessed by many components (e.g., `AuthContext` for user session).
-   `react-hook-form` & `Zod`: For form data management, validation, and submission.
-   `useActionState` (React 19): For handling Server Action responses and managing form submission feedback.
-   `useFormStatus` (React 19): For accessing the pending status of the last form submission within a form.

### Routing Architecture

#### Route Organization

The application utilizes **Next.js App Router**, where routing is file-system based. Each folder inside the `app` directory represents a segment of the route, and a `page.tsx` file defines the UI for that route. Routes are logically grouped by feature or user role (e.g., `(auth)`, `dashboard`).

```plaintext
frontend/app/
├── (auth)/                   # Route group for authentication pages
│   ├── login/                # /login
│   │   └── page.tsx
│   ├── register/             # /register
│   │   └── page.tsx
│   └── layout.tsx            # Auth-specific layout
├── dashboard/                # /dashboard
│   └── page.tsx
├── cvs/                      # /cvs (for job seeker)
│   ├── upload/
│   │   └── page.tsx
│   ├── history/
│   │   └── page.tsx
│   └── layout.tsx
├── jobs/                     # /jobs (for talent seeker)
│   ├── jd/
│   │   ├── upload/
│   │   │   └── page.tsx
│   │   └── match/
│   │       └── page.tsx
│   └── layout.tsx
└── layout.tsx                # Root layout
```

#### Protected Route Pattern

Protected routes ensure that only authenticated and authorized users can access certain parts of the application. This is typically implemented within `layout.tsx` files or in page components using Next.js Middleware or by performing authentication checks at the Server Component level.

```typescript
// app/dashboard/layout.tsx (Server Component)
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth'; // A server-side function to get session from cookie

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession(); // This function would read the access_token cookie
  if (!session) {
    redirect('/login'); // Redirect unauthenticated users
  }

  // Assuming session object contains user role for authorization
  // if (session.user.role !== 'admin') {
  //   redirect('/unauthorized');
  // }

  return (
    <div className="flex">
      {/* Sidebar, Header, etc. */}
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

### Frontend Services Layer

#### API Client Setup

All backend API interactions are centralized in `src/services/api-client.ts`, using `axios`. This client is configured to include credentials automatically, and critically, handles the `access_token` cookie for both client-side and server-side requests.

```typescript
// src/services/api-client.ts
import axios from 'axios';
import { getCookie } from 'cookies-next'; // Example for client-side access, if needed directly

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // IMPORTANT: Automatically includes cookies for client-side requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach cookie for SSR requests (e.g., from Server Actions/Server Components)
// This is a conceptual example and actual implementation depends on how Server Actions
// propagate request headers or contexts. For direct Server Component fetch,
// the cookie would be available in the request headers passed by Next.js.
apiClient.interceptors.request.use(config => {
  if (typeof window === 'undefined') { // Check if running on server-side
    // For Server Components/Actions, we need to manually forward the cookie
    // This is a simplified representation; in reality, the cookie needs to be
    // extracted from the incoming request's headers and explicitly set here.
    // The 'next/headers' module (cookies()) or a context-based approach might be used.
    const accessToken = getCookie('access_token'); // This would need to be from server-side context
    if (accessToken) {
        // Axios's withCredentials handles it, but for explicit control, or
        // if an Authorization header is strictly needed by backend for some reason:
        // config.headers.Authorization = `Bearer ${accessToken}`;
    }
  }
  return config;
});

// Error handling interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Standardized error handling, e.g., redirect to login on 401, show toast for other errors
    if (error.response?.status === 401) {
      // Redirect to login or refresh token logic
      console.error("Unauthorized, redirecting to login...");
      // window.location.href = '/login'; // Client-side redirect
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### Service Example

Each feature will have its own service file, abstracting API calls for that domain.

```typescript
// src/services/auth.service.ts
import apiClient from './api-client';
import { LoginPayload, RegisterPayload, User } from '@/types/user'; // Using global types

class AuthService {
  async login(payload: LoginPayload): Promise<User> {
    const response = await apiClient.post('/auth/login', payload);
    return response.data;
  }

  async register(payload: RegisterPayload): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/register', payload);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/users/me');
    return response.data;
  }

  // ... other auth related services
}

export const authService = new AuthService();
```

---
## Backend Architecture

This section describes the internal architecture of our Python-based backend, including service organization, data access patterns, and the authentication flow. We are using a traditional server approach to support the local Ollama LLM.

### Service Architecture

#### Traditional Server Architecture

The backend is a monolithic application with a modular design, running on a traditional server (e.g., a Linux VM). Each business feature (e.g., auth, cvs, jobs) is encapsulated within its own module, promoting a clean separation of concerns.

##### Controller/Route Organization
Routes are organized by feature into separate `router.py` files within each module. These routers are then aggregated in the main `main.py` file. This keeps the API definitions clean and organized by domain.

```plaintext
backend/app/
├── main.py               # Main application entry point, includes all routers
└── modules/
    ├── auth/
    │   └── router.py       # Contains /auth/* endpoints
    ├── users/
    │   └── router.py       # Contains /users/* endpoints
    ├── cvs/
    │   └── router.py       # Contains /cvs/* endpoints
    └── jobs/
        └── router.py       # Contains /jobs/* endpoints
```

##### Controller Template
A standard router file defines API endpoints using FastAPI's decorators and depends on the service layer for business logic.

```python
# backend/app/modules/cvs/router.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from . import schemas, service

router = APIRouter(prefix="/cvs", tags=["CVs"])

@router.post("/", response_model=schemas.CV, status_code=201)
async def upload_cv(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """
    Upload a new CV for the current user.
    Initiates AI analysis in a background task.
    """
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are accepted.")

    new_cv = await service.create_cv(db=db, user=current_user, file=file)
    return new_cv

@router.get("/", response_model=List[schemas.CV])
async def get_user_cvs(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all CVs uploaded by the current user.
    """
    cvs = await service.get_cvs_by_user(db=db, user_id=current_user.id)
    return cvs

# ... other CV endpoints
```

### Database Architecture

#### Schema Design
The database schema is designed for PostgreSQL and includes tables for `users`, `cvs`, and `job_descriptions`. It utilizes `pgvector` for semantic search and appropriate indexes for performance.

```sql
-- Assumes the 'pgvector' extension is installed: CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_content JSONB,
    summary TEXT,
    quality_score INTEGER,
    ats_compatibility_feedback TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    extracted_skills TEXT[],
    total_experience_years INTEGER,
    embedding VECTOR(768)
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    required_skills TEXT[],
    min_experience_years INTEGER,
    location_type VARCHAR(50) NOT NULL CHECK (location_type IN ('remote', 'hybrid', 'on-site')),
    salary_min INTEGER,
    salary_max INTEGER,
    embedding VECTOR(768)
);

-- Indexes are defined on all foreign keys, vector columns, and commonly filtered fields.
```

#### Data Access Layer
A **Repository Pattern** (realized as a "Service Layer") is used to abstract all database interactions. The `router` layer calls the `service` layer, which in turn interacts with the SQLAlchemy `models`. This separates business logic from API routing and improves testability.

```python
# backend/app/modules/cvs/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import UploadFile
import shutil
import uuid

from . import models, schemas
from app.modules.users.models import User
from app.core.ai_service import process_cv_in_background # Fictional AI service call

async def create_cv(db: AsyncSession, user: User, file: UploadFile):
    # 1. Save file to disk
    file_extension = file.filename.split('.')[-1]
    file_id = uuid.uuid4()
    file_path = f"/path/to/storage/{file_id}.{file_extension}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Create DB entry
    db_cv = models.CV(
        user_id=user.id,
        filename=file.filename,
        file_path=file_path,
        # Other fields will be populated by the AI task
    )
    db.add(db_cv)
    await db.commit()
    await db.refresh(db_cv)

    # 3. Trigger background AI processing
    process_cv_in_background(cv_id=db_cv.id, file_path=file_path)

    return db_cv

async def get_cvs_by_user(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(models.CV)
        .where(models.CV.user_id == user_id, models.CV.is_active == True)
        .order_by(models.CV.uploaded_at.desc())
    )
    return result.scalars().all()
```

### Authentication and Authorization

#### Auth Flow
The authentication flow uses HttpOnly cookies for security, which is ideal for web applications and SSR contexts.

```mermaid
sequenceDiagram
    participant Client
    participant API_Gateway as API Gateway/FastAPI
    participant DB as PostgreSQL DB

    Client->>API_Gateway: POST /auth/login (username, password)
    activate API_Gateway
    API_Gateway->>DB: Find user by email
    activate DB
    DB-->>API_Gateway: User record (with hashed_password)
    deactivate DB
    API_Gateway->>API_Gateway: Verify password against hash (using Passlib)
    alt Password is valid
        API_Gateway->>API_Gateway: Create access_token and refresh_token (JWTs)
        API_Gateway-->>Client: 200 OK (Set-Cookie: access_token, Set-Cookie: refresh_token)
    else Password is invalid
        API_Gateway-->>Client: 401 Unauthorized (Error: Invalid credentials)
    end
    deactivate API_Gateway
```

#### Middleware/Guards
FastAPI uses a dependency injection system to protect endpoints. A `get_current_user` dependency is injected into any protected route. This function is responsible for reading the `access_token` cookie, validating the JWT, and retrieving the corresponding user from the database.

```python
# backend/app/modules/auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.users import service as user_service
from app.modules.users.models import User

# This tells FastAPI to look for a cookie named 'access_token'
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(cookie_scheme)
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await user_service.get_user(db=db, user_id=user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user
```

---
## Unified Project Structure

```plaintext
datn/
├── apps/                       # Application packages
│   ├── frontend/               # Next.js frontend application
│   │   ├── app/                # App Router: pages, layouts, routes
│   │   ├── components/         # Shared React components (including shadcn/ui)
│   │   ├── features/           # Feature-specific components and logic
│   │   ├── lib/                # Frontend utilities (cn, etc.)
│   │   ├── services/           # API client services (e.g., auth.service.ts)
│   │   ├── public/             # Static assets
│   │   ├── next.config.ts      # Next.js configuration
│   │   └── package.json
│   │
│   └── backend/                # FastAPI backend application
│       ├── alembic/            # Database migrations
│       ├── app/                # Main application source code
│       │   ├── core/           # Core components (config, database, security)
│       │   ├── modules/        # Feature modules (auth, users, cvs, jobs)
│       │   ├── templates/      # Email templates
│       │   └── main.py         # Application entry point
│       ├── tests/              # Backend tests
│       ├── alembic.ini         # Alembic configuration
│       └── requirements.txt    # Python dependencies
│
├── packages/                   # Shared packages within the monorepo
│   └── shared-types/           # TypeScript types shared between FE/BE
│       ├── src/
│       │   ├── index.ts        # Main export file
│       │   ├── user.ts         # User related types
│       │   ├── cv.ts           # CV related types
│       │   └── job.ts          # Job related types
│       └── package.json
│
├── .github/                    # CI/CD workflows (e.g., GitHub Actions)
│   └── workflows/
│       ├── frontend-ci.yaml
│       └── backend-ci.yaml
│
├── docs/                       # Project documentation
│   ├── prd.md
│   └── architecture.md
│
├── .gitignore
├── package.json                # Root package.json (defines npm workspaces)
└── README.md
```

---
## Development Workflow

### **Revised `Development Workflow` (Updated for Ollama Model Installation)**

### Local Development Setup

#### Prerequisites

Before starting, ensure the following tools are installed on your system:

```bash
# 1. Node.js (v20 or higher) and npm
# 2. Python (v3.11 or higher)
# 3. Docker and Docker Compose (for running PostgreSQL and Ollama)
# 4. Git (for version control)
```

#### Initial Setup

Follow these steps to set up the project for the first time:

```bash
# 1. Clone the repository
git clone <repository_url>
cd datn

# 2. Install frontend and shared package dependencies
npm install

# 3. Set up the backend environment
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# 4. Set up environment variables
# In `apps/frontend/`, create a .env.local file.
# In `apps/backend/`, create a .env file.
# (See 'Required Environment Variables' section below for details)

# 5. Start local infrastructure (PostgreSQL and Ollama)
# Ensure Docker is running, then from the root directory:
docker-compose up -d # Assumes a docker-compose.yml is created for this

# 6. CRITICAL: Install required AI models into Ollama
# The Ollama container starts empty. Run these commands to pull the models.
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama pull nomic-embed-text

# 7. Run database migrations
# From the `apps/backend` directory with the venv activated:
alembic upgrade head
```

#### Development Commands

To run the application, you will need two separate terminals.

```bash
# Terminal 1: Start the Frontend (from the root directory)
npm run dev --workspace=frontend
# Frontend will be available at http://localhost:3000

# Terminal 2: Start the Backend (from the apps/backend directory, with venv activated)
uvicorn app.main:app --reload
# Backend API will be available at http://localhost:8000
```

### Environment Configuration

#### Required Environment Variables

```bash
# Frontend: apps/frontend/.env.local
#--------------------------------------
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1


# Backend: apps/backend/.env
#--------------------------------------
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/datn_db

# JWT Secret and Algorithm
SECRET_KEY=your_super_secret_key_that_is_at_least_32_chars_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Service Configuration
OLLAMA_API_BASE_URL=http://localhost:11434

# Email SMTP Configuration (example)
MAIL_USERNAME=apikey
MAIL_PASSWORD=your_smtp_api_key
MAIL_FROM=noreply@yourdomain.com
MAIL_PORT=587
MAIL_SERVER=smtp.yourprovider.net
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

---
## Deployment Architecture

This section defines the deployment strategy for getting the full-stack application into staging and production environments, based on our chosen platform architecture (Vercel for Frontend, Self-Hosted for Backend).

### Deployment Strategy

**Frontend Deployment:**
-   **Platform:** **Vercel**
-   **Build Command:** `npm run build`
-   **Output Directory:** `.next`
-   **CDN/Edge:** Handled automatically by Vercel's global edge network. Deployment is triggered by a `git push` to the main branch.

**Backend Deployment:**
-   **Platform:** **Self-Hosted Linux Server** (e.g., AWS EC2, DigitalOcean Droplet)
-   **Deployment Method:**
    1.  Provision a Linux server with Docker, Python, and NGINX.
    2.  Set up a production PostgreSQL database and Ollama service (likely via Docker Compose).
    3.  Create a non-root user for running the application.
    4.  Clone the repository onto the server.
    5.  Set up the Python virtual environment and install dependencies from `requirements.txt`.
    6.  Set up environment variables for production.
    7.  Run the FastAPI application using a production-grade server like **Gunicorn** with Uvicorn workers (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`).
    8.  Configure **NGINX** as a reverse proxy to forward requests to the Gunicorn process and handle SSL termination.
    9.  Run database migrations (`alembic upgrade head`).

### CI/CD Pipeline

A CI/CD pipeline automates testing and deployment. We will use a combination of Vercel's built-in CI/CD and GitHub Actions.

```yaml
# .github/workflows/backend-ci.yaml
# This pipeline runs on every push or pull request to the main branch for the backend.
# It does NOT handle deployment, which remains a manual process for the backend in this MVP.

name: Backend CI

on:
  push:
    branches: [ main ]
    paths:
      - 'apps/backend/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'apps/backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip --upgrade pip
        pip install -r apps/backend/requirements.txt
        pip install ruff pytest # Install testing tools

    - name: Lint with Ruff
      run: |
        ruff check apps/backend/

    - name: Run tests with Pytest
      run: |
        # This step would require a test database setup in CI
        # For now, it's a placeholder for running unit tests that don't need a DB
        pytest apps/backend/tests/
```

**Frontend CI/CD Note:** Vercel automatically handles CI/CD for the frontend. When the project's Git repository is connected to Vercel, every `git push` to the `main` branch will trigger a new build and deployment. Pull requests will automatically get their own preview deployments.

### Environments

| Environment | Frontend URL | Backend URL | Purpose |
| :--- | :--- | :--- | :--- |
| Development | `http://localhost:3000` | `http://localhost:8000` | Local development and testing by developers. |
| Staging | `https://staging.yourdomain.com` | `https://staging-api.yourdomain.com` | Pre-production environment for QA and UAT. A replica of production. |
| Production | `https://www.yourdomain.com` | `https://api.yourdomain.com` | Live environment for end-users. |

---
## Security and Performance

### Security Requirements

#### Frontend Security

-   **CSP Headers (Content Security Policy):** Implement a strict CSP to mitigate XSS (Cross-Site Scripting) and data injection attacks. This will whitelist trusted sources for scripts, styles, images, and other resources.
-   **XSS Prevention:** Leverage React's automatic escaping of content and sanitize all user-generated content rendered in the UI. Ensure any dynamic HTML rendering is done cautiously.
-   **Secure Storage:** Avoid storing sensitive user information (like JWTs or personal data) in browser `localStorage` or `sessionStorage`. Session tokens (`access_token`, `refresh_token`) will be managed via HttpOnly, Secure cookies, which are automatically sent with requests but inaccessible to client-side JavaScript.

#### Backend Security

-   **Input Validation:** All incoming request data will be rigorously validated using Pydantic models in FastAPI. This prevents common vulnerabilities like SQL injection, XSS, and buffer overflows.
-   **Rate Limiting:** Implement rate limiting on sensitive endpoints (e.g., login, registration, password reset, CV uploads) using `fastapi-limiter` or `slowapi` to prevent brute-force attacks and resource exhaustion.
-   **CORS Policy:** Strictly configure CORS (Cross-Origin Resource Sharing) in FastAPI to only allow requests from the trusted frontend origins (e.g., `http://localhost:3000` for development, and the production frontend domain). `allow_credentials` will be set to `True` to allow cookies to be sent.

#### Authentication Security

-   **Token Storage:** `access_token` and `refresh_token` will be stored in HttpOnly and Secure cookies. This prevents JavaScript access to the tokens, mitigating XSS risks.
-   **Session Management:** Implement short-lived `access_token`s (e.g., 30 minutes) and longer-lived `refresh_token`s (e.g., 7 days). Utilize a refresh token rotation strategy to enhance security by invalidating older refresh tokens.
-   **Password Policy:** Enforce a strong password policy for user registration and password changes, requiring a minimum length, combination of character types (uppercase, lowercase, numbers, symbols), and protection against common passwords. Passwords are hashed using `bcrypt` (via `passlib`) before storage.

### Performance Optimization

#### Frontend Performance

-   **Bundle Size Target:** Aim to keep JavaScript and CSS bundle sizes minimal through code splitting, tree-shaking, and lazy loading components/routes. Use Next.js's built-in optimizations.
-   **Loading Strategy:** Leverage Next.js's Server-Side Rendering (SSR) and Static Site Generation (SSG) capabilities for optimal initial page load performance and SEO. Use `next/image` component for efficient image loading and optimization.
-   **Caching Strategy:** Utilize HTTP caching headers (Cache-Control, ETag) for static assets. Vercel's CDN automatically caches frontend assets at the edge for global users.

#### Backend Performance

-   **Response Time Target:** Critical API endpoints (e.g., CV upload, JD upload, `users/me`) should aim for a response time under 500ms for 95% of requests (NFR3).
-   **Database Optimization:** Ensure all frequently queried columns are appropriately indexed. Optimize SQL queries using `EXPLAIN ANALYZE`. Implement connection pooling with SQLAlchemy to efficiently manage database connections.
-   **Caching Strategy:** Integrate Redis (as proposed in Tech Stack) for caching frequently accessed data (e.g., user profiles, common configuration) to reduce database load and improve response times.

---
## Testing Strategy

### Testing Pyramid

Our testing strategy will follow the testing pyramid approach, emphasizing a large number of fast, isolated unit tests, a moderate number of integration tests, and a small number of broad end-to-end tests.

```plaintext
          E2E Tests
         /         \
   Integration Tests
  /                 \
Frontend Unit    Backend Unit
```

### Test Organization

Tests will be organized alongside the code they validate, ensuring discoverability and maintainability.

#### Frontend Tests
Frontend unit and integration tests (using Jest and React Testing Library) will be co-located with the components or features they test. This means test files will live in the same directory as the source files, often with a `.test.ts` or `.spec.ts` suffix.

```plaintext
frontend/
└── features/
    └── auth/
        ├── components/
        │   ├── LoginForm.tsx
        │   └── LoginForm.test.tsx  # Unit/Integration test for LoginForm
        ├── hooks/
        │   ├── useAuth.ts
        │   └── useAuth.test.ts
        └── actions.ts
```

#### Backend Tests
Backend tests (using Pytest and HTTPX) will be organized within a dedicated `apps/backend/tests` directory, mirroring the application's module structure. This makes it easy to find tests for specific services or endpoints.

```plaintext
backend/
└── apps/backend/
    └── tests/
        ├── modules/
        │   ├── auth/
        │   │   └── test_auth_router.py
        │   │   └── test_auth_service.py
        │   └── cvs/
        │       └── test_cv_router.py
        │       └── test_cv_service.py
        └── conftest.py  # Pytest fixtures
```

#### E2E Tests
End-to-End (E2E) tests (using Playwright) will reside in a separate top-level `e2e` directory. These tests simulate real user interactions across the entire deployed application.

```plaintext
datn/
└── e2e/
    ├── specs/
    │   ├── auth.spec.ts        # E2E tests for login, registration
    │   └── cv_upload.spec.ts   # E2E tests for CV upload flow
    └── playwright.config.ts
```

### Test Examples

#### Frontend Component Test (Jest & React Testing Library)

```typescript
// frontend/features/auth/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from './LoginForm';
import { loginAction } from '../actions'; // Mock this action

// Mock the Server Action
jest.mock('../actions', () => ({
  loginAction: jest.fn(),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    (loginAction as jest.Mock).mockReset();
  });

  it('renders email and password fields', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('calls loginAction with form data on submit', async () => {
    (loginAction as jest.Mock).mockResolvedValueOnce({}); // Mock successful login

    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(loginAction).toHaveBeenCalledTimes(1);
      expect(loginAction).toHaveBeenCalledWith(expect.any(FormData));
      // You can further assert specific FormData content if needed
    });
  });
});
```

#### Backend API Test (Pytest & HTTPX)

```python
# backend/apps/backend/tests/modules/auth/test_auth_router.py
import pytest
from httpx import AsyncClient
from main import app # Assuming app instance is importable

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, test_db): # test_db fixture for isolated DB
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200 # Or 201 Created depending on actual implementation
    assert "message" in response.json() # Assuming it returns a success message

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, create_test_user): # create_test_user fixture
    email, password = create_test_user # From fixture

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies # Check for HttpOnly cookie
    assert "refresh_token" in response.cookies
```

#### E2E Test (Playwright)

```typescript
// e2e/specs/cv_upload.spec.ts
import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('CV Upload Flow', () => {
  test('should allow a logged-in user to upload a CV', async ({ page }) => {
    // 1. Log in the user
    await page.goto('/login');
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'securepassword123');
    await page.click('button[type="submit"]');

    // Wait for successful login and redirection to dashboard
    await page.waitForURL('/dashboard');
    expect(page.url()).toContain('/dashboard');

    // 2. Navigate to CV Upload page
    await page.click('a[href="/cvs/upload"]');
    await page.waitForURL('/cvs/upload');

    // 3. Upload a CV file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(__dirname, '../test-data/sample_cv.pdf'));

    await page.click('button:has-text("Upload CV")');

    // 4. Verify success message or redirection
    await expect(page.locator('text=CV Uploaded, Analysis Pending...')).toBeVisible();

    // Optionally, wait and check for analysis completion if feasible within E2E
    // await page.waitForSelector('text=Analysis Complete', { timeout: 60000 });
  });
});
```

---
## Coding Standards

### Critical Fullstack Rules

-   **Type Sharing:** All TypeScript types and interfaces shared between the frontend and backend API (e.g., data models, API payloads) **must** be defined in the `packages/shared-types` package and imported from there. Do not redefine types in the frontend.
-   **API Calls:** All frontend API interactions **must** be channeled through the centralized `API Service Layer` (`/services`). Never make direct `fetch` or `axios` calls from UI components.
-   **Backend Modularity:** All new backend logic **must** be encapsulated within a feature module in `apps/backend/app/modules/`. Each module must follow the `router.py`, `service.py`, `schemas.py`, `models.py` pattern.
-   **Cookie Security:** Do not attempt to read or write authentication tokens from client-side JavaScript. Rely on `HttpOnly` cookies and the backend to manage the session. The frontend must use `withCredentials: true` (or the equivalent) for all API calls.
-   **Environment Variables:** Access environment variables only through a dedicated configuration module (e.g., `app/core/config.py` in the backend). Never access `process.env` directly within frontend components or backend business logic.
-   **State Updates:** In React components, never mutate state directly. Always use the setter function from `useState` or dispatch actions for reducers.

### Naming Conventions

| Element | Frontend Convention | Backend Convention | Example |
| :--- | :--- | :--- | :--- |
| Components (React) | `PascalCase` | N/A | `UserProfile.tsx` |
| Hooks (React) | `camelCase` with `use` prefix | N/A | `useAuth.ts` |
| API Routes | N/A | `kebab-case` | `/api/v1/user-profile` |
| Database Tables | N/A | `snake_case` (plural) | `user_profiles`, `cvs` |
| Python Variables/Functions | N/A | `snake_case` | `get_current_user` |
| Python Classes | N/A | `PascalCase` | `class AuthService:` |
| TypeScript Types/Interfaces | `PascalCase` | N/A | `interface UserProfile {}` |

---
## Error Handling Strategy

### Error Flow

This diagram illustrates the flow when the backend validation fails for an API request.

```mermaid
sequenceDiagram
    participant Frontend_Client as Frontend (Client)
    participant API_Gateway as API Gateway/FastAPI
    participant Pydantic as Pydantic Validator

    Frontend_Client->>API_Gateway: POST /api/v1/cvs (with invalid payload)
    activate API_Gateway
    API_Gateway->>Pydantic: Validates request body against schema
    activate Pydantic
    Pydantic-->>API_Gateway: Validation fails, raises RequestValidationError
    deactivate Pydantic
    API_Gateway->>API_Gateway: Catches exception via custom handler
    API_Gateway-->>Frontend_Client: 422 Unprocessable Entity (with structured JSON error)
    deactivate API_Gateway
    Frontend_Client->>Frontend_Client: Parses JSON error and displays field-specific messages to the user
```

### Error Response Format

To ensure consistency, all API errors will adhere to the following JSON structure. This provides a machine-readable error code, a human-readable message, and optional details for field-specific validation errors.

```typescript
interface ApiError {
  error: {
    code: string; // e.g., 'VALIDATION_ERROR', 'UNAUTHENTICATED', 'RESOURCE_NOT_FOUND'
    message: string; // User-friendly error message
    details?: Record<string, any>; // For field-specific validation errors
    timestamp: string; // ISO 8601 timestamp
  };
}

// Example for a validation error:
// {
//   "error": {
//     "code": "VALIDATION_ERROR",
//     "message": "One or more fields are invalid.",
//     "details": {
//       "email": "A user with this email already exists.",
//       "password": "Password must be at least 8 characters long."
//     },
//     "timestamp": "2025-12-10T10:00:00Z"
//   }
// }
```

### Frontend Error Handling

Errors will be handled globally in the frontend's `API Service Layer` using an `axios` response interceptor. This centralizes error logic and makes UI components cleaner.

```typescript
// src/services/api-client.ts (interceptor part)
import axios from 'axios';

const apiClient = axios.create({ /* ... */ });

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (axios.isAxiosError(error) && error.response) {
      const apiError = error.response.data as ApiError;
      const status = error.response.status;

      switch (status) {
        case 401:
          // Unauthorized: User is not logged in or token expired.
          // Redirect to login page.
          console.error("Unauthorized access. Redirecting...", apiError.error.message);
          window.location.href = '/login'; // Or use Next.js router
          break;
        case 403:
          // Forbidden: User is logged in but lacks permissions.
          console.error("Forbidden access.", apiError.error.message);
          // Redirect to an 'unauthorized' page.
          break;
        case 422:
          // Validation Error: Let the calling function handle field-specific errors.
          console.warn("Validation error:", apiError.error.details);
          break;
        default:
          // Generic server error (5xx)
          console.error("An unexpected server error occurred:", apiError.error.message);
          // Show a generic error toast/notification to the user.
          break;
      }
    } else {
      // Network error or other non-Axios error
      console.error("A network or unknown error occurred:", error.message);
    }
    // Propagate the error so that individual UI components can also react if needed.
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Backend Error Handling

In FastAPI, custom exception handlers will be used to catch specific errors and format them into our standard `ApiError` response.

```python
# backend/app/main.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone

app = FastAPI()

# Custom handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = {}
    for error in exc.errors():
        field = ".".join(map(str, error["loc"]))
        error_details[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "One or more fields are invalid.",
                "details": error_details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

# Custom handler for a generic application exception
class AppBaseException(Exception):
    def __init__(self, message: str, code: str = "GENERIC_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

# ... include routers and other app setup
```

---
## Monitoring and Observability

### Monitoring Stack

Our monitoring strategy uses a combination of platform-provided tools and dedicated services to get a complete picture of the application's health.

-   **Frontend Monitoring:** **Vercel Analytics**
    -   Provides real-time Core Web Vitals (LCP, FID, CLS) and page view metrics out-of-the-box. This gives us immediate insight into the real-world performance experienced by our users.

-   **Backend Monitoring:** **Prometheus + Grafana**
    -   **Prometheus** will be used to scrape and store time-series metrics from our self-hosted backend. A FastAPI Prometheus exporter will expose application metrics (like request latency and error rates).
    -   **Grafana** will be used to create dashboards to visualize the metrics collected by Prometheus, providing a real-time view of backend health.

-   **Error Tracking:** **Sentry**
    -   Sentry will be integrated into both the frontend and backend to capture, aggregate, and alert on exceptions in real-time. This provides much richer context than plain logs, including stack traces and user session data.

-   **Performance Monitoring:**
    -   Frontend performance is covered by Vercel Analytics.
    -   Backend API performance (latency, throughput) will be monitored via Prometheus and Grafana.

### Key Metrics

We will focus on the following key metrics to measure the health and performance of our application.

#### Frontend Metrics

-   **Core Web Vitals:** LCP (Largest Contentful Paint), FID (First Input Delay), CLS (Cumulative Layout Shift).
-   **JavaScript Error Rate:** Percentage of user sessions that encounter a JavaScript error (tracked by Sentry).
-   **API Latency (Client-side):** The time it takes for API requests to complete from the user's browser perspective.
-   **User Interactions:** Tracking key user flows (e.g., CV upload initiated, job search performed) to understand feature adoption.

#### Backend Metrics

-   **Request Rate:** Requests per second/minute to the API.
-   **Error Rate:** Percentage of 4xx and 5xx HTTP status codes, particularly focusing on the 5xx server error rate.
-   **API Endpoint Latency:** 95th and 99th percentile response times for all major API endpoints.
-   **Database Performance:** Slow query rate, active connections, and cache hit ratio.
-   **AI Service Performance:**
    -   **Inference Latency:** p95 latency for both the `llama3.1:8b` (generation) and `nomic-embed-text` (embedding) models.
    -   **Resource Utilization:** GPU and RAM utilization of the server hosting the Ollama service (collected via `node_exporter` for Prometheus).

---
## Checklist Results Report

```

Task: Analyze the potentially_problematic_string. If it's syntactically invalid due to incorrect escaping (e.g., "\n", "\t", "\\", "\'", '"'), correct the invalid syntax. The goal is to ensure the text will be a valid and correctly interpreted.

For example, if potentially_problematic_string is "bar\nbaz", the corrected_new_string_escaping should be "bar\nbaz".
If potentially_problematic_string is console.log(\"Hello World\"), it should be console.log("Hello World").

Return ONLY the corrected string in the specified JSON format with the key 'corrected_string_escaping'. If no escaping correction is needed, return the original potentially_problematic_string.
```