# AI Recruitment Platform

This is a full-stack AI-powered recruitment platform.

## Overview

The project consists of three main parts:

*   **Frontend:** A Next.js application (port 3000)
*   **Backend:** A FastAPI (Python) application (port 8000)
*   **Socket.io Server:** A Node.js WebSocket server for real-time messaging (port 3001)

The system is designed to provide intelligent features like AI matching, CV parsing, and real-time chat between recruiters and job seekers.

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

## Socket.io Server

The Socket.io server handles real-time messaging between recruiters and job seekers.

**Quick Start:**
```bash
cd socket-server
./start.sh       # Khởi động server
./stop.sh        # Dừng server
./restart.sh     # Khởi động lại
```

**Manual Start:**
```bash
cd socket-server
npm install      # Lần đầu tiên
node server.js > /tmp/socket-server.log 2>&1 &
```

**Check Status:**
```bash
lsof -i :3001                          # Kiểm tra server đang chạy
tail -f /tmp/socket-server.log         # Xem log
```

For more details, see the `socket-server/README.md`.

## 🚀 Quick Start - Khởi động toàn bộ hệ thống

```bash
# Terminal 1: Backend
cd backend
source ~/miniconda3/envs/backend312/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Socket.io Server
cd socket-server
./start.sh
```

**Kiểm tra tất cả servers:**
```bash
ps aux | grep -E "uvicorn|next dev|node server"
```

**Dừng tất cả:**
```bash
pkill -f uvicorn
pkill -f "next dev"
cd socket-server && ./stop.sh
```
