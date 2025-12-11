# Technology Stack

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
