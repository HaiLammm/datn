# Debug Session Status - Job Applicants Chat Feature

**Last Updated:** 2026-01-07 14:37 ICT  
**Session:** Fixing "Failed to fetch conversation" error

---

## 🎯 Current Objective
Resolve the 500 Internal Server Error when loading chat conversation page at `/messages/[conversationId]`

## ✅ Issues Fixed (Completed)

### 1. Socket.io Server Not Running ✅
- **Status:** RESOLVED
- **PID:** ~51580 (may vary)
- **Port:** 3001
- **Log:** `/tmp/socket-server.log`
- **Helper Scripts:** `socket-server/{start,stop,restart}.sh`

### 2. Missing Backend Endpoint ✅
- **Status:** RESOLVED (endpoint existed, was misconfigured)
- **Endpoint:** `GET /api/v1/messages/conversations/{conversation_id}`
- **Location:** `backend/app/modules/messages/router.py:93-126`

### 3. Display "User" Instead of Real Names ✅
- **Status:** RESOLVED
- **Files Modified:**
  - `backend/app/modules/messages/schemas.py` - Unified `UserBasicInfo` schema
  - `backend/app/modules/messages/models.py` - Added relationships
  - `backend/app/modules/messages/service.py` - Updated user info population
  - `frontend/app/messages/[conversationId]/page.tsx` - Extract name from API

### 4. NEXT_REDIRECT Error on "Start Chat" ✅
- **Status:** RESOLVED
- **Root Cause:** Server Actions with `redirect()` cannot be awaited in client components
- **Solution:** Changed to `router.push()` instead
- **File:** `frontend/app/jobs/jd/[jdId]/applicants/page.tsx:182`

### 5. Pydantic Validation Error ✅
- **Status:** RESOLVED
- **Root Cause:** Duplicate `UserBasicInfo` definitions with conflicting fields
- **Solution:** Removed duplicate, unified to single schema with all required fields
- **File:** `backend/app/modules/messages/schemas.py`

---

## 🔴 Current Issue (IN PROGRESS)

### Issue 6: "Failed to fetch conversation" Error
**Status:** INVESTIGATING with enhanced logging  
**Priority:** HIGH

#### Symptoms:
```
Error fetching conversation: Error: Failed to fetch conversation
POST /messages/7c68ae22-5399-42cd-bab3-117958a48aff 500
```

#### What We Know:
✅ **Conversation Exists:**
```sql
id: 7c68ae22-5399-42cd-bab3-117958a48aff
recruiter_id: 11 (luonghaimal@gmail.com, role: recruiter)
candidate_id: 14 (teamgamozxv@gmail.com, role: job_seeker)
```

✅ **All Servers Running:**
- Backend: Port 8000 (PID 54535) - Responding OK
- Frontend: Port 3000 (Next.js v16.0.5) - Running
- Socket.io: Port 3001 - Running

✅ **Backend Schema Correct:**
- Single `UserBasicInfo` schema with fields: `id, full_name, email, role, avatar`
- `ConversationResponse` includes `recruiter` and `candidate` objects
- Service method populates all fields correctly

#### Recent Changes (Current Session):
1. ✅ Added detailed error logging to `getConversationWithContext()`:
   - Location: `frontend/features/messages/actions.ts:254-264`
   - Now logs: HTTP status code, error response body
   - Better error messages with context

#### Next Steps to Debug:
1. **Visit chat page** to trigger error with new logging
2. **Check browser console** for detailed error output
3. **Check backend logs** for Python traceback
4. **Test backend endpoint directly** with curl

#### Test Commands:
```bash
# Check conversation in DB
PGPASSWORD=12070123a psql -U luonghailam -d datn -c \
  "SELECT * FROM conversations WHERE id = '7c68ae22-5399-42cd-bab3-117958a48aff';"

# Test backend endpoint (need valid JWT token)
curl -v http://localhost:8000/api/v1/messages/conversations/7c68ae22-5399-42cd-bab3-117958a48aff \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Check backend process
lsof -i :8000

# View backend logs (if available)
tail -f /tmp/backend.log
```

---

## 📂 Key Files Modified This Session

### Backend:
1. `backend/app/modules/messages/schemas.py`
   - Lines 18-25: Unified `UserBasicInfo` schema
   - Removed duplicate at lines 132-138

2. `backend/app/modules/messages/models.py`
   - Added `recruiter` and `candidate` relationships to `Conversation` model

3. `backend/app/modules/messages/service.py`
   - Lines 237-299: Updated `get_conversation_by_id()` with user info population
   - Line 530: Updated field names in `get_conversation_list_for_user()`

### Frontend:
1. `frontend/features/messages/actions.ts`
   - Lines 254-264: Enhanced error logging in `getConversationWithContext()`
   - Line 85-87: Deprecated `navigateToConversation()`

2. `frontend/app/jobs/jd/[jdId]/applicants/page.tsx`
   - Line 182: Changed from Server Action to `router.push()`

3. `frontend/app/messages/[conversationId]/page.tsx`
   - Lines 86-96: Extract user names from API response

---

## 🔍 Potential Root Causes to Investigate

### High Priority:
1. **JWT Token Decode Issue**
   - Location: `frontend/features/messages/actions.ts:240-242`
   - Check if `jwtDecode()` is returning correct `user_id`

2. **SQLAlchemy Relationship Loading**
   - Location: `backend/app/modules/messages/service.py:256-263`
   - Verify `selectinload()` works correctly with async session

3. **Type Mismatch**
   - Frontend expects string IDs in some places
   - Backend returns integer IDs
   - Could cause comparison issues at line 273-275 of actions.ts

### Medium Priority:
4. **Circular Import**
   - `service.py:253` imports `User` model
   - Could cause issues in some edge cases

5. **Database Connection**
   - Async session might be timing out
   - Check if connection pool is healthy

---

## 🗂️ Database Schema Reference

### conversations table:
```sql
id              UUID PRIMARY KEY
recruiter_id    INTEGER REFERENCES users(id)
candidate_id    INTEGER REFERENCES users(id)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### users table:
```sql
id              SERIAL PRIMARY KEY
email           VARCHAR UNIQUE NOT NULL
full_name       VARCHAR
role            VARCHAR (job_seeker, recruiter, admin)
avatar          VARCHAR
is_active       BOOLEAN
```

### messages table:
```sql
id              UUID PRIMARY KEY
conversation_id UUID REFERENCES conversations(id)
sender_id       INTEGER REFERENCES users(id)
content         TEXT
created_at      TIMESTAMP
is_read         BOOLEAN
```

---

## 🧪 Testing Checklist

- [ ] Browser console shows detailed error with HTTP status
- [ ] Backend logs show Python traceback (if available)
- [ ] Direct curl test of backend endpoint
- [ ] JWT token decodes correctly
- [ ] User IDs match between frontend and backend
- [ ] Database query returns expected data
- [ ] Socket.io connection works after page loads

---

## 📝 Environment Info

- **Backend:** Python 3.13.9, FastAPI, PostgreSQL
- **Frontend:** Next.js 16.0.5 with Turbopack
- **Socket.io:** Node.js server on port 3001
- **Database:** PostgreSQL (datn)
- **Auth:** JWT tokens in HttpOnly cookies

---

## 🎓 Key Learnings

1. **Server Actions with redirect()** throw NEXT_REDIRECT error when awaited in client components
   - Solution: Use `router.push()` instead from client

2. **Duplicate Pydantic schemas** cause validation errors
   - Python uses last definition in file
   - Always check for duplicates when getting field validation errors

3. **SQLAlchemy relationships** need `selectinload()` for eager loading in async contexts
   - Prevents N+1 queries and relationship loading issues

4. **Error logging is critical** for debugging async/server-action issues
   - Added detailed logging at every fetch point
   - Log status codes, error bodies, and context

---

## 👤 Who to Ask for Help

If stuck:
1. Check OpenCode docs: https://opencode.ai/docs
2. Review BMAD agents: See `AGENTS.md`
3. Use `bmad-master` agent for complex multi-step debugging
4. Use `dev` agent for implementation fixes

---

**Next Action:** Test the chat page and review the enhanced error logs to identify exact failure point.
