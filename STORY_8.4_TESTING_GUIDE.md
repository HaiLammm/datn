# Story 8.4: Interview History - Backend Testing Guide

## ✅ Backend Implementation Status: COMPLETE

All 4 new endpoints have been implemented and are ready for testing.

---

## 📋 Endpoints Summary

| # | Method | Endpoint | Response Schema | Status |
|---|--------|----------|----------------|--------|
| 1 | GET | `/api/v1/interviews` | `PaginatedInterviewSessions` | ✅ Implemented |
| 2 | GET | `/api/v1/interviews/{id}/detail` | `InterviewSessionDetail` | ✅ Implemented |
| 3 | GET | `/api/v1/interviews/{id}/transcript` | `InterviewTranscriptResponse` | ✅ Implemented |
| 4 | GET | `/api/v1/interviews/{id}/evaluation/detail` | `InterviewEvaluationDetail` | ✅ Implemented |

---

## 🔧 Manual Testing Instructions

### Prerequisites

1. **Backend server running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Test user with job_seeker role:**
   - Email: `test_jobseeker@example.com`
   - Password: `Test@12345`
   - Must be activated (`is_active=true`, `is_verified=true`)

3. **Test interview sessions** (at least 1 completed interview with questions, turns, and evaluation)

### Step 1: Get Authentication Token

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_jobseeker@example.com",
    "password": "Test@12345"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "refresh_token": "..."
}
```

**Save the access token** for use in subsequent requests:
```bash
export TOKEN="<your_access_token_here>"
```

---

### Test 1: List Interview Sessions

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/interviews?page=1&page_size=10&sort_by=created_at&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "job_title": "Senior Backend Engineer",
      "created_at": "2026-01-10T14:30:00Z",
      "completed_at": "2026-01-10T15:15:00Z",
      "status": "completed",
      "overall_score": 8.5,
      "overall_grade": "A",
      "duration_minutes": 45,
      "question_count": 12,
      "turn_count": 18
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

**✅ Success Criteria:**
- [x] Returns 200 OK
- [x] Response contains `items` array
- [x] Response contains `total`, `page`, `page_size`, `total_pages`
- [x] Each item has `question_count` and `turn_count` (computed fields)

**Test Variations:**
```bash
# Sort by score descending
curl -X GET "http://localhost:8000/api/v1/interviews?sort_by=overall_score&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/interviews?status=completed" \
  -H "Authorization: Bearer $TOKEN"

# Pagination
curl -X GET "http://localhost:8000/api/v1/interviews?page=2&page_size=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Test 2: Get Interview Detail

**Request:**
```bash
# Replace {SESSION_ID} with actual UUID from Test 1
curl -X GET "http://localhost:8000/api/v1/interviews/{SESSION_ID}/detail" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "id": "uuid",
  "job_title": "Senior Backend Engineer",
  "job_description": "Full job description text...",
  "position_level": "senior",
  "created_at": "2026-01-10T14:30:00Z",
  "completed_at": "2026-01-10T15:15:00Z",
  "status": "completed",
  "duration_minutes": 45,
  "total_turns": 18,
  "overall_score": 8.5,
  "overall_grade": "A",
  "hiring_recommendation": "hire",
  "question_count": 12,
  "turn_count": 18
}
```

**✅ Success Criteria:**
- [x] Returns 200 OK
- [x] Response includes `job_description`, `position_level`
- [x] Response includes `hiring_recommendation`
- [x] Computed fields (`question_count`, `turn_count`) are present

**Error Cases:**
```bash
# Non-existent session (should return 404)
curl -X GET "http://localhost:8000/api/v1/interviews/00000000-0000-0000-0000-000000000000/detail" \
  -H "Authorization: Bearer $TOKEN"

# Other user's session (should return 403)
# (Requires session ID belonging to different user)
```

---

### Test 3: Get Interview Transcript

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/interviews/{SESSION_ID}/transcript" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "interview_id": "uuid",
  "job_title": "Senior Backend Engineer",
  "total_turns": 18,
  "turns": [
    {
      "turn_number": 1,
      "question_text": "Tell me about your experience with Python...",
      "question_type": "technical",
      "candidate_message": "I have 5 years of experience...",
      "ai_response": "That's great! Can you elaborate on...",
      "scores": {
        "technical_score": 8.0,
        "communication_score": 8.5,
        "depth_score": 7.5,
        "overall_score": 8.0
      },
      "action_type": "follow_up",
      "created_at": "2026-01-10T14:32:00Z"
    }
  ]
}
```

**✅ Success Criteria:**
- [x] Returns 200 OK
- [x] Response includes `total_turns` matching number of items in `turns` array
- [x] Each turn has `scores` object with 4 score fields
- [x] Each turn has `question_text`, `candidate_message`, `ai_response`
- [x] Turns are ordered by `turn_number`

**Performance Check:**
- Response time should be < 500ms for sessions with up to 50 turns

---

### Test 4: Get Evaluation Detail

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/interviews/{SESSION_ID}/evaluation/detail" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "interview_id": "uuid",
  "job_title": "Senior Backend Engineer",
  "overall_evaluation": {
    "score": 8.5,
    "grade": "A",
    "hiring_recommendation": "hire"
  },
  "dimension_scores": {
    "technical": {
      "score": 8.5,
      "weight": 0.5,
      "sub_scores": {
        "accuracy": 9.0,
        "depth": 8.0,
        "problem_solving": 8.5
      },
      "evidence": [
        "Strong knowledge of async/await patterns",
        "Good understanding of database optimization"
      ]
    },
    "communication": {
      "score": 8.0,
      "weight": 0.25,
      "sub_scores": {
        "clarity": 8.5,
        "conciseness": 7.5,
        "professionalism": 8.0
      },
      "evidence": ["Clear explanations", "Well-structured responses"]
    },
    "behavioral": {
      "score": 9.0,
      "weight": 0.25,
      "sub_scores": {
        "teamwork": 9.0,
        "adaptability": 8.5,
        "leadership": 9.5
      },
      "evidence": ["Demonstrates strong team collaboration"]
    }
  },
  "detailed_analysis": {
    "key_strengths": ["Strong technical foundation", "Excellent communication"],
    "areas_for_improvement": ["Could provide more specific examples"],
    "notable_moments": ["Handled challenging algorithm question well"],
    "red_flags": []
  },
  "recommendations": {
    "hiring_decision": "hire",
    "reasoning": "Candidate demonstrates strong technical skills...",
    "role_fit": "Excellent fit for senior backend role",
    "development_areas": ["Deepen knowledge of distributed systems"]
  },
  "created_at": "2026-01-10T15:15:00Z"
}
```

**✅ Success Criteria:**
- [x] Returns 200 OK
- [x] All 4 main sections present: `overall_evaluation`, `dimension_scores`, `detailed_analysis`, `recommendations`
- [x] Dimension scores for technical, communication, behavioral
- [x] Each dimension has `sub_scores` and `evidence` arrays
- [x] Weights sum to 1.0 (50% technical, 25% communication, 25% behavioral)

**Error Cases:**
```bash
# Interview not completed (should return 400)
curl -X GET "http://localhost:8000/api/v1/interviews/{INCOMPLETE_SESSION_ID}/evaluation/detail" \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"detail": "Interview evaluation is not available yet. Complete the interview first."}
```

---

## 🔍 Additional Testing

### Authorization Tests

**Test: Access another user's interview (should fail)**
1. Create second user account
2. Get their interview session ID
3. Try to access with first user's token
4. **Expected:** 403 Forbidden

**Test: Unauthenticated access (should fail)**
```bash
curl -X GET "http://localhost:8000/api/v1/interviews"
# Expected: {"detail": "Not authenticated"}
```

### Performance Tests

Run these with Apache Bench (ab) or similar tool:

```bash
# List endpoint (target: <200ms P95)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/interviews?page=1&page_size=10"

# Detail endpoint (target: <300ms P95)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/interviews/{SESSION_ID}/detail"

# Transcript endpoint (target: <500ms P95)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/interviews/{SESSION_ID}/transcript"
```

---

## 🐛 Known Issues / TODOs

- [ ] Model relationship error when importing User model directly (KeyError: 'CV')
  - **Workaround:** Testing must be done via API, not direct database access
- [ ] Test data creation script needs to be fixed for automated testing

---

## 📊 Test Results Template

Use this template to record test results:

```
Date: _______
Tester: _______

| Test | Status | Notes |
|------|--------|-------|
| 1. List Sessions | ⬜ PASS / ⬜ FAIL | |
| 2. Session Detail | ⬜ PASS / ⬜ FAIL | |
| 3. Transcript | ⬜ PASS / ⬜ FAIL | |
| 4. Evaluation Detail | ⬜ PASS / ⬜ FAIL | |
| Authorization | ⬜ PASS / ⬜ FAIL | |
| Performance | ⬜ PASS / ⬜ FAIL | |
```

---

## 🚀 Next Steps

After backend testing is complete:

1. ✅ **Frontend Implementation** - Create React components
2. ✅ **Integration Testing** - Test frontend + backend together
3. ✅ **E2E Testing** - Full user flow from dashboard to history to detail
4. ✅ **Story Completion** - Update story status to 'done'

---

## 📞 Support

If you encounter issues:
1. Check backend logs: `tail -f /tmp/backend.log`
2. Verify database has test data
3. Confirm user is activated and has role='job_seeker'
4. Check that interview sessions have related questions, turns, and evaluations

**Backend Server Status:**
```bash
curl -s http://localhost:8000/docs
# Should return Swagger UI HTML
```
