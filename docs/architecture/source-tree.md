# Unified Project Structure

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