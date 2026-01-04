# Deployment Architecture

This section defines the deployment strategy for getting the full-stack application into staging and production environments, based on our chosen platform architecture (Vercel for Frontend, Self-Hosted for Backend).

## Deployment Strategy

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

## CI/CD Pipeline

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

## Environments

| Environment | Frontend URL | Backend URL | Purpose |
| :--- | :--- | :--- | :--- |
| Development | `http://localhost:3000` | `http://localhost:8000` | Local development and testing by developers. |
| Staging | `https://staging.yourdomain.com` | `https://staging-api.yourdomain.com` | Pre-production environment for QA and UAT. A replica of production. |
| Production | `https://www.yourdomain.com` | `https://api.yourdomain.com` | Live environment for end-users. |

---