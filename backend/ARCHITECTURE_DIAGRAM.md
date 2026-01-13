# Async Question Generation - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  User Action: Create Interview                             │     │
│  └──────────────────────────┬────────────────────────────────┘     │
│                              │                                       │
│  ┌──────────────────────────▼────────────────────────────────┐     │
│  │  createInterviewAction()                                   │     │
│  │  - Calls POST /interviews                                  │     │
│  │  - Gets session_id + status='pending'                      │     │
│  │  - Starts polling loop                                     │     │
│  └──────────────────────────┬────────────────────────────────┘     │
│                              │                                       │
│  ┌──────────────────────────▼────────────────────────────────┐     │
│  │  pollInterviewStatus()                                     │     │
│  │  - Polls GET /interviews/{id}/status every 3s              │     │
│  │  - Max 60 attempts (3 minutes timeout)                     │     │
│  └──────────────────────────┬────────────────────────────────┘     │
│                              │                                       │
│  ┌──────────────────────────▼────────────────────────────────┐     │
│  │  <QuestionGenerationProgress />                            │     │
│  │  - Shows: pending → generating → ready                     │     │
│  │  - Displays progress bar, elapsed time                     │     │
│  │  - Shows error messages if failed                          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                ▲
                                │ HTTP Requests
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  POST /api/v1/interviews                                   │     │
│  │  ────────────────────────────────────                      │     │
│  │  1. Create session (status='pending')                      │     │
│  │  2. Save to database                                       │     │
│  │  3. Trigger Celery task (non-blocking)                     │     │
│  │  4. Return 202 Accepted (~200ms)                           │     │
│  └─────────────────────────┬─────────────────────────────────┘     │
│                             │                                        │
│                             │ Triggers                               │
│                             ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  GET /api/v1/interviews/{id}/status                          │   │
│  │  ──────────────────────────────────────────                 │   │
│  │  1. Query session from database                              │   │
│  │  2. Return current status + questions (if ready)             │   │
│  │  3. Response time: ~50ms                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  GET /api/v1/interviews/health/celery                         │   │
│  │  ────────────────────────────────────────────                │   │
│  │  1. Check Celery workers (inspect.stats())                   │   │
│  │  2. Check Redis connection (ping)                            │   │
│  │  3. Return health status                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Task Queue
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        REDIS (Message Broker)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  Queue: interviews_queue                                │         │
│  │  ─────────────────────────                              │         │
│  │  [Task 1: generate_questions_task]                      │         │
│  │  [Task 2: generate_questions_task]                      │         │
│  │  [Task 3: generate_questions_task]                      │         │
│  └────────────────────────────────────────────────────────┘         │
│                                                                       │
│  Port: 6379                                                          │
│  Docker: redis:7-alpine                                              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Worker Pulls Task
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CELERY WORKER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  generate_questions_task()                                   │   │
│  │  ─────────────────────────────────────                       │   │
│  │                                                               │   │
│  │  Step 1: Update status='generating'                          │   │
│  │          └─> UPDATE interview_sessions SET status='...'      │   │
│  │                                                               │   │
│  │  Step 2: Initialize AI Agent                                 │   │
│  │          └─> QuestionGeneratorAgent(config)                  │   │
│  │                                                               │   │
│  │  Step 3: Generate Questions (2-3 minutes)                    │   │
│  │          └─> agent.generate_questions(...)                   │   │
│  │              ├─> Call Ollama API                             │   │
│  │              ├─> Parse response                              │   │
│  │              └─> Return structured questions                 │   │
│  │                                                               │   │
│  │  Step 4: Save to Database                                    │   │
│  │          └─> INSERT INTO interview_questions (...)           │   │
│  │                                                               │   │
│  │  Step 5: Log Agent Call                                      │   │
│  │          └─> INSERT INTO agent_call_logs (...)               │   │
│  │                                                               │   │
│  │  Step 6: Update status='ready'                               │   │
│  │          └─> UPDATE interview_sessions SET status='ready'    │   │
│  │                                                               │   │
│  │  Error Handling:                                             │   │
│  │  - Network/timeout errors → Retry (up to 2 times)           │   │
│  │  - Exponential backoff: 30s, 60s, 120s                      │   │
│  │  - Update status='error' on final failure                    │   │
│  │                                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  Concurrency: 2 tasks in parallel                                    │
│  Timeouts: 10 min hard, 9 min soft                                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Calls
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OLLAMA (AI Service)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Model: llama3.1:8b (or configured model)                           │
│  API: http://localhost:11434/api/generate                           │
│  Response Time: 10-15 seconds per question                          │
│  Total Time: 2-3 minutes for 10 questions                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Results
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        POSTGRESQL (Database)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  interview_sessions                                         │    │
│  │  ────────────────────────────────────                       │    │
│  │  id (UUID)                                                  │    │
│  │  candidate_id (INT)                                         │    │
│  │  status (TEXT)  ← 'pending' → 'generating' → 'ready'       │    │
│  │  error_message (TEXT)  ← NULL or error details             │    │
│  │  created_at, updated_at                                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  interview_questions                                        │    │
│  │  ────────────────────────────────────                       │    │
│  │  id (UUID)                                                  │    │
│  │  interview_session_id (UUID) ← FK                          │    │
│  │  question_text (TEXT)                                       │    │
│  │  category, difficulty, key_points                          │    │
│  │  evaluation_criteria, ideal_answer_outline                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  agent_call_logs                                            │    │
│  │  ────────────────────────────────────                       │    │
│  │  id (UUID)                                                  │    │
│  │  agent_type (TEXT) ← 'question_generator'                  │    │
│  │  interview_session_id (UUID) ← FK                          │    │
│  │  status (TEXT) ← 'success' or 'error'                      │    │
│  │  latency_ms (INT) ← Task execution time                    │    │
│  │  error_message (TEXT) ← NULL or error details              │    │
│  │  created_at                                                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Status Flow State Machine

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     │ POST /interviews
     │ (Create session)
     ▼
┌──────────┐
│ pending  │  ← Session created, task queued
└────┬─────┘
     │
     │ Celery worker picks up task
     │ (Usually < 5 seconds)
     ▼
┌──────────────┐
│ generating   │  ← AI is generating questions
└────┬─────────┘  (2-3 minutes)
     │
     ├────► Success?
     │
     ├─── YES ──────►  ┌────────┐
     │                 │ ready  │  ← Questions saved ✅
     │                 └────────┘
     │
     └─── NO ───────►  ┌────────┐
                       │ error  │  ← Generation failed ❌
                       └────────┘  (error_message populated)
```

---

## Retry Logic Flow

```
Task Execution
     │
     ├─► Success? ──YES──► Update status='ready' ──► DONE ✅
     │
     └─► Error
           │
           ├─► Is Retryable?
           │   (timeout, network, ollama connection)
           │
           ├─── YES ───► Attempt count?
           │             │
           │             ├─► Attempt 1 ─► Wait 30s  ──► RETRY
           │             ├─► Attempt 2 ─► Wait 60s  ──► RETRY
           │             └─► Attempt 3 ─► Wait 120s ──► RETRY
           │                              │
           │                              └─► Max retries reached
           │                                  │
           └─── NO ────────────────────────────┘
                                                │
                                                ▼
                                    Update status='error' ❌
                                    Save error_message
                                    Log to agent_call_logs
                                    DONE (Failed)
```

---

## Monitoring Dashboard (Celery Flower)

```
┌─────────────────────────────────────────────────────────────────┐
│  Celery Flower - http://localhost:5555                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Workers                                                         │
│  ───────────────────────────────────────────────────────────    │
│  celery@hostname         [ONLINE]         Processed: 42          │
│                                                                   │
│  Tasks                                                           │
│  ───────────────────────────────────────────────────────────    │
│  Task Name                    State      Received    Runtime     │
│  generate_questions_task      SUCCESS    10:00:05    149.2s      │
│  generate_questions_task      RUNNING    10:02:45    45.3s       │
│  generate_questions_task      PENDING    10:03:12    -           │
│                                                                   │
│  Broker                                                          │
│  ───────────────────────────────────────────────────────────    │
│  Redis                        [ONLINE]                           │
│  URL: redis://localhost:6379/0                                   │
│  Queue Length: 3                                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Performance Timeline

```
Time (seconds)
0                        30                   60                   180
│                        │                    │                    │
├─POST /interviews       │                    │                    │
│ (200ms)                │                    │                    │
│                        │                    │                    │
├─Return 202 Accepted    │                    │                    │
│  status='pending'      │                    │                    │
│                        │                    │                    │
│                        │                    │                    │
├─Celery picks up task   │                    │                    │
│ (< 5s)                 │                    │                    │
│                        │                    │                    │
├─Status: 'generating' ──┼────────────────────┼────────────────────┤
│                        │                    │                    │
│ [AI Generating...]     │                    │                    │
│ - Question 1 (15s)     │                    │                    │
│ - Question 2 (15s)     │                    │                    │
│ - Question 3 (15s) ────┤                    │                    │
│ - Question 4 (15s)     │                    │                    │
│ - Question 5 (15s)     │                    │                    │
│ - Question 6 (15s) ────┤────────────────────┤                    │
│ - Question 7 (15s)     │                    │                    │
│ - Question 8 (15s)     │                    │                    │
│ - Question 9 (15s)     │                    │                    │
│ - Question 10 (15s) ───┼────────────────────┤                    │
│                        │                    │                    │
│ [Saving to DB...]      │                    │                    │
│                        │                    │                    │
└─Status: 'ready' ───────┼────────────────────┼────────────────────┘
  (149s total)           │                    │
                         │                    │
Frontend Polling:        │                    │
├─Poll 1 (3s): pending   │                    │
├─Poll 2 (6s): generating│                    │
├─Poll 3 (9s): generating│                    │
├─Poll 4 (12s): generating                    │
...                      │                    │
├─Poll 50 (150s): ready ─┘                    │
└─Stop polling                                │
```

---

## Key Takeaways

✅ **Non-Blocking**: API returns in 200ms, not 270 seconds  
✅ **Scalable**: Unlimited concurrent requests (queued)  
✅ **Resilient**: Automatic retries with exponential backoff  
✅ **Observable**: Health checks, Celery Flower, database logs  
✅ **User-Friendly**: Progress indicator, time estimates, error messages  

---

**Next Step:** Start Celery worker and test the system!

```bash
cd backend
./scripts/start_async_services.sh
```
