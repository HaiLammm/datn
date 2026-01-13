# Async Question Generation - Quick Reference

## 🚀 Quick Start

```bash
# Start all services
cd backend
./scripts/start_async_services.sh

# Or manually:
# Terminal 1: Redis (if not running)
docker run -d --name redis-datn -p 6379:6379 redis:7-alpine

# Terminal 2: Celery Worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=2

# Terminal 3: FastAPI
uvicorn app.main:app --reload --port 8000

# Terminal 4: Celery Flower (optional monitoring)
celery -A app.core.celery_app flower --port=5555
```

---

## 📡 API Endpoints

### Create Interview (Async)
```http
POST /api/v1/interviews
Content-Type: application/json
Authorization: Bearer {token}

{
  "job_description": "Backend Developer...",
  "cv_content": "John Doe, 5 years...",
  "position_level": "senior",
  "num_questions": 10
}

Response: 202 Accepted
{
  "session": {"id": "uuid", "status": "pending"},
  "questions": [],
  "message": "Questions are being generated..."
}
```

### Check Generation Status
```http
GET /api/v1/interviews/{session_id}/status
Authorization: Bearer {token}

Response: 200 OK
{
  "status": "generating",  // pending → generating → ready
  "session_id": "uuid",
  "message": "Questions are being generated...",
  "questions": []  // Populated when status is 'ready'
}
```

### Health Check
```http
GET /api/v1/interviews/health/celery

Response: 200 OK
{
  "status": "healthy",
  "celery": {"worker_count": 1, "workers": [...]},
  "redis": {"connected": true}
}
```

---

## 🔄 Status Flow

```
pending → generating → ready (success)
                    ↘ error (failure)
```

### Status Meanings
- **pending**: Session created, task queued
- **generating**: AI is generating questions
- **ready**: Questions generated successfully ✅
- **error**: Generation failed ❌

---

## 🎯 Frontend Integration

### Server Action (Polling)
```typescript
import { createInterviewAction } from '@/features/interviews/actions';

const result = await createInterviewAction({
  job_description: "...",
  cv_content: "...",
  position_level: "senior",
  num_questions: 10
});

// Polls automatically every 3s until ready
// Returns when status is 'ready' or throws error
```

### UI Component
```typescript
import { QuestionGenerationProgress } from '@/components/interviews/QuestionGenerationProgress';

<QuestionGenerationProgress
  status={status}  // 'pending' | 'generating' | 'ready' | 'error'
  errorMessage={error}
  elapsedTime={elapsedTime}
  estimatedTimeRemaining={180 - elapsedTime}
/>
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Settings
```python
# backend/app/core/celery_app.py
task_time_limit = 600  # 10 minutes hard limit
task_soft_time_limit = 540  # 9 minutes soft limit
worker_prefetch_multiplier = 2
worker_max_tasks_per_child = 100
```

---

## 🐛 Debugging

### Check Services
```bash
# Redis
redis-cli ping  # Should return PONG

# Celery Workers
celery -A app.core.celery_app inspect active

# Task Queue
redis-cli LLEN celery
```

### View Logs
```bash
# Celery Worker (in terminal where it's running)
# Shows: task received, status updates, completion

# Celery Flower Dashboard
http://localhost:5555
# Navigate to "Tasks" to see all tasks

# Database Logs
SELECT * FROM agent_call_logs ORDER BY created_at DESC LIMIT 10;
```

### Common Issues

**❌ "No active workers"**
```bash
# Start Celery worker
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

**❌ "Redis connection refused"**
```bash
# Start Redis
docker start redis-datn
# Or: redis-server
```

**❌ "Task timeout"**
- Check Ollama is running: `curl http://localhost:11434/api/version`
- Increase time limits in `celery_app.py`
- Reduce `num_questions` in request

---

## 📊 Monitoring

### Celery Flower
```
http://localhost:5555
- View all tasks (success/failure)
- Monitor worker status
- See task execution time
- Inspect task arguments and results
```

### Health Check
```bash
# Check system health
curl http://localhost:8000/api/v1/interviews/health/celery | jq

# Expected output
{
  "status": "healthy",
  "celery": {"worker_count": 1},
  "redis": {"connected": true}
}
```

### Database Queries
```sql
-- Interview sessions by status
SELECT status, COUNT(*) 
FROM interview_sessions 
GROUP BY status;

-- Recent agent calls
SELECT agent_type, status, latency_ms, created_at
FROM agent_call_logs
ORDER BY created_at DESC
LIMIT 20;

-- Failed generations
SELECT id, status, error_message, created_at
FROM interview_sessions
WHERE status = 'error'
ORDER BY created_at DESC;
```

---

## ⏱️ Performance Benchmarks

| Operation | Expected Time |
|-----------|---------------|
| POST /interviews | < 500ms |
| GET /status | < 200ms |
| Question generation (10q) | 2-3 minutes |
| Celery task overhead | < 500ms |

---

## 🧪 Testing

```bash
# Quick test
curl -X POST http://localhost:8000/api/v1/interviews \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Backend Developer...",
    "cv_content": "John Doe...",
    "position_level": "middle",
    "num_questions": 10
  }'

# Save session ID from response
SESSION_ID="uuid-here"

# Poll status (repeat until ready)
curl http://localhost:8000/api/v1/interviews/$SESSION_ID/status \
  -H "Authorization: Bearer TOKEN"
```

**Full testing guide:** See `TESTING_ASYNC.md`

---

## 📁 Key Files

```
backend/
├── app/
│   ├── core/
│   │   ├── celery_app.py           # Celery configuration
│   │   └── config.py                # Redis settings
│   └── modules/interviews/
│       ├── tasks.py                 # Background tasks
│       ├── router.py                # API endpoints
│       ├── service.py               # Business logic
│       └── models.py                # Database models
├── scripts/
│   └── start_async_services.sh      # Service startup script
├── ASYNC_SETUP.md                   # Setup guide
└── TESTING_ASYNC.md                 # Testing guide

frontend/
├── components/interviews/
│   └── QuestionGenerationProgress.tsx  # UI component
├── features/interviews/
│   ├── actions.ts                    # Server actions
│   └── types.ts                      # TypeScript types
└── services/
    └── interview.service.ts          # API client
```

---

## 🔗 Useful Links

- **API Docs**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555
- **Setup Guide**: `backend/ASYNC_SETUP.md`
- **Testing Guide**: `backend/TESTING_ASYNC.md`

---

## 💡 Tips

1. **Always check Redis first** if tasks aren't running
2. **Use Flower** for visual monitoring and debugging
3. **Check Celery logs** for detailed error messages
4. **Poll every 3 seconds** in frontend (balance UX vs load)
5. **Set realistic timeouts** (AI generation takes 2-3 minutes)
6. **Monitor `agent_call_logs`** for debugging AI issues

---

## 🆘 Support

If you encounter issues:
1. Check health endpoint: `/interviews/health/celery`
2. Review Celery worker logs
3. Check `agent_call_logs` table for error details
4. Verify Ollama is running and responsive
5. See `TESTING_ASYNC.md` for troubleshooting guide
