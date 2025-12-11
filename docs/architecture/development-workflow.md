# Development Workflow

## **Revised `Development Workflow` (Updated for Ollama Model Installation)**

## Local Development Setup

### Prerequisites

Before starting, ensure the following tools are installed on your system:

```bash
# 1. Node.js (v20 or higher) and npm
# 2. Python (v3.11 or higher)
# 3. Docker and Docker Compose (for running PostgreSQL and Ollama)
# 4. Git (for version control)
```

### Initial Setup

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

### Development Commands

To run the application, you will need two separate terminals.

```bash
# Terminal 1: Start the Frontend (from the root directory)
npm run dev --workspace=frontend
# Frontend will be available at http://localhost:3000

# Terminal 2: Start the Backend (from the apps/backend directory, with venv activated)
uvicorn app.main:app --reload
# Backend API will be available at http://localhost:8000
```

## Environment Configuration

### Required Environment Variables

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