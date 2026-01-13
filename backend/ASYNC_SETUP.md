# Async Question Generation - Setup Guide

## Overview

Epic 8 Interview Room now uses **async background job processing** with **Celery + Redis** to avoid timeout issues when generating interview questions.

### Architecture

```
User Request → FastAPI → Celery Task (Background) → Ollama AI → Database
     ↓                        ↓
  Returns immediately    (2-3 minutes processing)
     ↓                        ↓
Frontend polls status   Updates DB status: pending → generating → ready
```

## Prerequisites

- Python 3.10+
- PostgreSQL
- Redis (for Celery message broker)
- Ollama (for AI models)

---

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `celery>=5.3.0` - Distributed task queue
- `redis>=5.0.0` - Message broker and result backend

---

## 2. Install & Start Redis

### Option A: Docker (Recommended)

```bash
docker run -d \
  --name redis-datn \
  -p 6379:6379 \
  redis:7-alpine
```

### Option B: Native Installation

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Expected output: PONG
```

---

## 3. Environment Configuration

Add to `.env`:

```env
# Celery & Redis (Epic 8 Async)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=your_password  # Optional, if Redis has auth
```

---

## 4. Database Migration

Apply the new migration for async status tracking:

```bash
cd backend
alembic upgrade head
```

This adds:
- `error_message` column to `interview_sessions` table
- New status values: `'generating'`, `'ready'`, `'error'`

---

## 5. Start Celery Worker

Open a **new terminal** and run:

```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

**For development (with auto-reload):**
```bash
watchmedo auto-restart --directory=./app --pattern='*.py' --recursive \
  -- celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

**Production (with systemd):**
Create `/etc/systemd/system/celery-datn.service`:
```ini
[Unit]
Description=Celery Worker for DATN
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/datn/backend
Environment="PATH=/path/to/venv/bin:$PATH"
ExecStart=/path/to/venv/bin/celery -A app.core.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --pidfile=/var/run/celery/celery.pid \
  --logfile=/var/log/celery/celery.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start celery-datn
sudo systemctl enable celery-datn
```

---

## 6. Start Application

```bash
# Terminal 1: FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery worker (already running from step 5)

# Terminal 3: Frontend (if needed)
cd frontend
npm run dev
```

---

## 7. Verify Setup

### Check Redis Connection

```bash
redis-cli
> ping
PONG
> quit
```

### Check Celery Worker

In Celery terminal, you should see:
```
celery@hostname v5.3.0 (emerald-rush)

.> app:         datn_workers:0x...
.> transport:   redis://localhost:6379/0
.> results:     redis://localhost:6379/0
.> concurrency: 2 (prefork)

[tasks]
  . app.modules.interviews.tasks.generate_questions_task

[INFO] Connected to redis://localhost:6379/0
[INFO] mingle: searching for neighbors
[INFO] mingle: all alone
[INFO] celery@hostname ready.
```

### Test Question Generation

```bash
curl -X POST http://localhost:8000/api/v1/interviews \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Backend Developer with Python and FastAPI experience...",
    "cv_content": "Nguyen Van A, 3 years experience with Python...",
    "position_level": "middle",
    "num_questions": 5
  }'
```

**Expected Response (202 Accepted):**
```json
{
  "session": {
    "id": "uuid-here",
    "status": "pending",
    ...
  },
  "questions": [],
  "message": "Interview session created. Questions are being generated..."
}
```

**Poll Status:**
```bash
curl http://localhost:8000/api/v1/interviews/{session_id}/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Status Flow:**
1. `pending` (initial)
2. `generating` (Celery task running)
3. `ready` (questions generated) OR `error` (if failed)

---

## 8. Monitoring & Troubleshooting

### Monitor Celery Tasks

```bash
# In separate terminal
celery -A app.core.celery_app flower --port=5555
```

Open http://localhost:5555 to see task dashboard.

### Check Redis Keys

```bash
redis-cli
> KEYS *
> GET celery-task-meta-<task_id>
```

### Common Issues

**Issue: "Connection refused" to Redis**
- Check Redis is running: `sudo systemctl status redis`
- Check port: `netstat -tuln | grep 6379`
- Check firewall rules

**Issue: Celery worker not picking up tasks**
- Verify worker is running: check terminal output
- Check task registration: look for task name in worker startup
- Restart worker: `Ctrl+C` then re-run celery command

**Issue: Tasks timeout**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is pulled: `ollama list`
- Increase timeout in `_sub-agents/configs/question_generator_config.json`:
  ```json
  {
    "ollama_settings": {
      "timeout": 180  // Increase to 3 minutes
    }
  }
  ```

**Issue: Frontend stuck in "generating" status**
- Check Celery worker logs for errors
- Check `agent_call_logs` table for error messages:
  ```sql
  SELECT * FROM agent_call_logs 
  WHERE interview_session_id = 'uuid-here' 
  ORDER BY created_at DESC;
  ```

---

## 9. Performance Tuning

### Celery Concurrency

Adjust based on your server:
- **Development:** `--concurrency=2`
- **Production (4 CPU cores):** `--concurrency=4`
- **Production (8+ cores):** `--concurrency=8`

### Redis Configuration

For production, edit `/etc/redis/redis.conf`:
```conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Ollama Optimization

**Use GPU if available:**
```bash
# Check GPU availability
nvidia-smi

# Ollama will auto-detect GPU
# Question generation: ~4s → ~0.5s with GPU
```

**Adjust model parameters** in `_sub-agents/configs/question_generator_config.json`:
```json
{
  "model_parameters": {
    "num_predict": 4096,  // Increase if questions get truncated
    "temperature": 0.6    // Lower = more consistent
  }
}
```

---

## 10. Production Deployment

### Supervisor Configuration (Alternative to systemd)

`/etc/supervisor/conf.d/celery-datn.conf`:
```ini
[program:celery-datn]
command=/path/to/venv/bin/celery -A app.core.celery_app worker --loglevel=info --concurrency=4
directory=/path/to/datn/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/celery.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery-datn
```

### Health Checks

Add to your monitoring system:
```bash
# Redis health
redis-cli ping || echo "Redis down!"

# Celery health (requires celery-flower)
curl http://localhost:5555/api/workers | jq '.[] | .status'
```

---

## API Changes Summary

### POST /interviews

**Before (Blocking):**
- Status: 201 Created
- Response time: ~3-5 seconds
- Returns: `{session, questions[], message}`

**After (Async):**
- Status: **202 Accepted**
- Response time: ~200ms
- Returns: `{session, questions: [], message}`

### NEW: GET /interviews/{id}/status

Poll this endpoint to check progress:
- `pending`: Task queued
- `generating`: AI processing
- `ready`: Questions ready (includes `questions[]`)
- `error`: Failed (includes `error_message`)

---

## Rollback Plan

If you need to revert to sync mode:

1. **Backend:** Change router to use `create_interview()` instead of `create_interview_async()`
2. **Frontend:** Remove polling logic from `actions.ts`
3. **No database rollback needed** - new columns are backward compatible

---

## Next Steps

- [ ] Add frontend loading UI for `generating` state (Task 8)
- [ ] Test end-to-end flow with real users (Task 9)
- [ ] Monitor Celery task performance in production
- [ ] Consider adding task progress updates (0%, 50%, 100%)
- [ ] Add alerts for failed tasks (email/Slack notifications)

---

## Support

**Documentation:**
- Celery: https://docs.celeryproject.org/
- Redis: https://redis.io/docs/
- Flower: https://flower.readthedocs.io/

**Logs:**
- Celery: `/var/log/celery/celery.log`
- Redis: `/var/log/redis/redis-server.log`
- FastAPI: `uvicorn` console output

**Contact:** Backend team / DevOps team
