# Epic 3: AI-Powered Candidate Discovery

## 3.1. Goals and Background Context

### 3.1.1. Goals

- Cho phep Talent Seekers (Recruiters) upload Job Descriptions (JD) de tim kiem ung vien
- Trien khai he thong ranking ung vien dua tren semantic matching voi JD
- Cung cap giao dien tim kiem ung vien bang ngon ngu tu nhien (semantic search)
- Hien thi match score chi tiet giua CV va JD voi breakdown ro rang
- Tao workflow cho Recruiter tu upload JD den shortlist ung vien

### 3.1.2. Background Context

He thong hien tai da co:
- CV upload va analysis cho Job Seekers (Epic 2 - da hoan thanh)
- Hybrid Skill Scoring voi skill extraction va matching foundation (Epic 5)
- Story 5.5 da implement backend skill-JD matching API (`/api/v1/cvs/{id}/match`)

Can bo sung:
- JD upload va storage module
- Candidate ranking/discovery engine
- Semantic search API
- Frontend cho Talent Seekers

**PRD Requirements Addressed:**
| Requirement | Description |
|-------------|-------------|
| **FR6** | Upload Job Description for candidate matching |
| **FR7** | Automatically rank candidates based on JD relevance |
| **FR8** | Natural language search for candidates (semantic) |
| **FR13** | Integrate JD upload and candidate search into UI |

### 3.1.3. Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-17 | 0.1.0 | Initial PRD draft for Candidate Discovery | John (PM) |

---

## 3.2. Requirements

### 3.2.1. Functional Requirements

| ID | Requirement |
|----|-------------|
| **FR-CD1** | He thong phai cho phep Talent Seekers upload JD duoi dang text hoac file (PDF/DOCX) |
| **FR-CD2** | He thong phai parse JD de extract required skills, experience requirements, va job details |
| **FR-CD3** | He thong phai luu tru JD voi metadata (title, description, required_skills, min_experience) |
| **FR-CD4** | He thong phai ranking tat ca CVs available dua tren relevance voi JD |
| **FR-CD5** | He thong phai tinh match_score (0-100) cho moi cap CV-JD |
| **FR-CD6** | He thong phai hien thi match breakdown: matched_skills, missing_skills, extra_skills |
| **FR-CD7** | He thong phai ho tro semantic search bang natural language query |
| **FR-CD8** | He thong phai tra ve top candidates voi relevance scores cho moi search |
| **FR-CD9** | Talent Seeker phai xem duoc danh sach JDs da upload |
| **FR-CD10** | Talent Seeker phai xem duoc candidate list cho moi JD |

### 3.2.2. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| **NFR-CD1** | Candidate ranking phai hoan thanh trong thoi gian chap nhan duoc cho demo |
| **NFR-CD2** | Semantic search phai tra ve ket qua relevant (manual validation) |
| **NFR-CD3** | UI phai consistent voi existing Job Seeker interface |
| **NFR-CD4** | API endpoints phai follow existing patterns (/api/v1/jobs/*) |

### 3.2.3. Compatibility Requirements

| ID | Requirement |
|----|-------------|
| **CR-CD1** | Integrate voi existing authentication system |
| **CR-CD2** | Su dung existing skill taxonomy tu Epic 5 |
| **CR-CD3** | Database schema phai compatible voi existing PostgreSQL setup |
| **CR-CD4** | Frontend phai su dung existing shadcn/ui components |

---

## 3.3. User Interface Enhancement Goals

### 3.3.1. New Screens Required

| Screen | Description |
|--------|-------------|
| **JD Upload Page** | Form upload JD (text input hoac file upload) |
| **JD List Page** | Danh sach JDs da upload voi status va actions |
| **JD Detail Page** | Chi tiet JD voi parsed requirements |
| **Candidate Results Page** | Ranked candidates cho JD voi match scores |
| **Candidate Search Page** | Semantic search interface |
| **Candidate Profile Modal** | Quick view CV summary va match details |

### 3.3.2. UI Flow

```
+-------------------------------------------------------------+
|                    Talent Seeker Dashboard                   |
+-------------------------------------------------------------+
|                                                             |
|  +---------------------+    +-----------------------------+ |
|  |  Upload New JD      |    |  Semantic Candidate Search  | |
|  |  [+ Add JD]         |    |  [Search box: "Python dev   | |
|  +---------------------+    |   with 3 years exp..."]     | |
|                             +-----------------------------+ |
|                                                             |
|  +-------------------------------------------------------------+
|  |  My Job Descriptions                                    |
|  |  +-----------------------------------------------------+|
|  |  | Senior Python Developer     |  15 matches  | View  ||
|  |  | Frontend React Engineer     |  8 matches   | View  ||
|  |  | DevOps Engineer            |  12 matches  | View  ||
|  |  +-----------------------------------------------------+|
|  +-------------------------------------------------------------+
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|            Candidate Results for "Senior Python Dev"        |
+-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  | #1  John Doe          Match: 92%   [View Profile]      |
|  |     v Python, FastAPI, PostgreSQL                      |
|  |     x Missing: Kubernetes                              |
|  +-------------------------------------------------------------+
|  | #2  Jane Smith        Match: 85%   [View Profile]      |
|  |     v Python, Django, MySQL                            |
|  |     x Missing: FastAPI, Docker                         |
|  +-------------------------------------------------------------+
+-------------------------------------------------------------+
```

---

## 3.4. Technical Assumptions

### 3.4.1. Database Schema

```sql
-- job_descriptions table (as defined in architecture.md)
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    required_skills TEXT[],
    min_experience_years INTEGER,
    location_type VARCHAR(50) CHECK (location_type IN ('remote', 'hybrid', 'on-site')),
    salary_min INTEGER,
    salary_max INTEGER,
    -- Parsed content from AI
    parsed_requirements JSONB,
    -- Optional: embedding for semantic search
    embedding VECTOR(768)
);

-- Candidate match results (optional caching table)
CREATE TABLE IF NOT EXISTS cv_jd_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE CASCADE,
    jd_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score INTEGER NOT NULL,
    matched_skills TEXT[],
    missing_skills TEXT[],
    extra_skills TEXT[],
    calculated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cv_id, jd_id)
);
```

### 3.4.2. API Endpoints

```yaml
# Job Description endpoints
POST   /api/v1/jobs/jd                    # Upload new JD
GET    /api/v1/jobs/jd                    # List user's JDs
GET    /api/v1/jobs/jd/{jd_id}            # Get JD details
DELETE /api/v1/jobs/jd/{jd_id}            # Delete JD
GET    /api/v1/jobs/jd/{jd_id}/candidates # Get ranked candidates for JD

# Semantic Search
POST   /api/v1/jobs/search                # Search candidates with natural language
```

### 3.4.3. New Files Structure

```
backend/app/modules/jobs/
+-- __init__.py
+-- models.py          # JobDescription, CVJDMatch models
+-- schemas.py         # JD input/output schemas
+-- service.py         # JD CRUD, matching logic
+-- router.py          # API endpoints
+-- jd_parser.py       # JD parsing with LLM

frontend/app/jobs/
+-- page.tsx           # Talent Seeker dashboard
+-- upload/
|   +-- page.tsx       # JD upload page
+-- [jdId]/
    +-- page.tsx       # JD detail + candidates
    +-- candidates/
        +-- page.tsx   # Full candidate list

frontend/features/jobs/
+-- components/
|   +-- JDUploadForm.tsx
|   +-- JDList.tsx
|   +-- JDCard.tsx
|   +-- CandidateList.tsx
|   +-- CandidateCard.tsx
|   +-- MatchBreakdown.tsx
|   +-- SemanticSearchBar.tsx
+-- actions.ts
+-- types.ts
```

---

## 3.5. User Stories

### Story 3.1: Job Description Module Foundation

**As a** developer,
**I want** JD database models and basic CRUD API,
**So that** JDs can be stored and managed.

#### Acceptance Criteria

1. Tao `JobDescription` SQLAlchemy model voi all fields tu schema
2. Tao Alembic migration cho `job_descriptions` table
3. Tao `JobDescriptionCreate`, `JobDescriptionResponse` Pydantic schemas
4. Implement CRUD endpoints: POST, GET (list), GET (detail), DELETE
5. Endpoints protected voi authentication
6. Basic validation: title required, description required

---

### Story 3.2: JD Parsing & Skill Extraction

**As a** system,
**I want** to parse JD content and extract requirements,
**So that** matching can be performed accurately.

#### Acceptance Criteria

1. Tao `JDParser` class su dung LLM
2. Extract `required_skills` tu JD text
3. Extract `min_experience_years` tu JD text
4. Extract `nice_to_have_skills` (optional)
5. Normalize skills su dung existing skill taxonomy
6. Store parsed results trong `parsed_requirements` JSONB field
7. Parsing chay async sau khi JD duoc upload

---

### Story 3.3: Candidate Ranking Engine

**As a** Talent Seeker,
**I want** candidates ranked by relevance to my JD,
**So that** I can quickly find the best matches.

#### Acceptance Criteria

1. Implement `CandidateRanker` class
2. Calculate match score (0-100) based on:
   - Skill overlap (weighted by importance)
   - Experience years match
   - Role/title relevance
3. Return ranked list voi match_score
4. Include breakdown: matched_skills, missing_skills, extra_skills
5. API endpoint: GET `/api/v1/jobs/jd/{jd_id}/candidates`
6. Support pagination (limit, offset)
7. Support filtering (min_score, skills)

---

### Story 3.4: Semantic Candidate Search

**As a** Talent Seeker,
**I want** to search candidates using natural language,
**So that** I can find relevant profiles without uploading a full JD.

#### Acceptance Criteria

1. Implement semantic search endpoint: POST `/api/v1/jobs/search`
2. Accept natural language query (e.g., "Python developer with AWS experience")
3. Parse query to extract search criteria
4. Match against CV skills va content
5. Return top N candidates voi relevance scores
6. Handle various query formats gracefully

---

### Story 3.5: JD Upload Frontend

**As a** Talent Seeker,
**I want** a user-friendly interface to upload JDs,
**So that** I can easily add job requirements.

#### Acceptance Criteria

1. Tao JD upload page voi form
2. Support text input (paste JD)
3. Support file upload (PDF/DOCX) - optional
4. Show parsing status (pending, processing, completed)
5. Display extracted requirements after parsing
6. Allow editing parsed requirements
7. Responsive design

---

### Story 3.6: Candidate Results Frontend

**As a** Talent Seeker,
**I want** to view matched candidates for my JD,
**So that** I can evaluate and shortlist them.

#### Acceptance Criteria

1. Tao candidate list page cho moi JD
2. Display candidates sorted by match score
3. Show match breakdown cho moi candidate
4. Color-coded match indicators (green/yellow/red)
5. Link to full CV analysis
6. Pagination support
7. Filter by minimum match score

---

### Story 3.7: Semantic Search Frontend

**As a** Talent Seeker,
**I want** a search interface for finding candidates,
**So that** I can quickly discover relevant profiles.

#### Acceptance Criteria

1. Tao search page voi search bar
2. Autocomplete/suggestions (optional)
3. Display search results voi relevance scores
4. Show brief candidate preview
5. Link to full profile
6. Search history (optional)

---

## 3.6. Implementation Priority

| Priority | Story | Rationale |
|----------|-------|-----------|
| **P0 - Must Have** | 3.1 JD Module Foundation | Base infrastructure |
| **P0 - Must Have** | 3.2 JD Parsing | Core functionality |
| **P0 - Must Have** | 3.3 Candidate Ranking | Core value proposition |
| **P1 - Should Have** | 3.5 JD Upload Frontend | User-facing feature |
| **P1 - Should Have** | 3.6 Candidate Results Frontend | User-facing feature |
| **P2 - Nice to Have** | 3.4 Semantic Search | Advanced feature |
| **P2 - Nice to Have** | 3.7 Search Frontend | Advanced feature |

---

## 3.7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| JD parsing accuracy | Medium | Medium | Use structured prompts, validate output |
| Candidate ranking fairness | Medium | Low | Transparent scoring, explainable results |
| Performance voi many CVs | High | Medium | Pagination, caching, async processing |
| LLM latency for search | Medium | High | Cache common queries, optimize prompts |

---

## 3.8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| JD upload success rate | >95% | System logs |
| Skill extraction accuracy | Acceptable for demo | Manual review |
| Candidate ranking relevance | Top 5 candidates relevant | Manual evaluation |
| Search results relevance | Meaningful results for queries | Manual testing |

---

## 3.9. Dependencies

| Story | Depends On |
|-------|------------|
| 3.2 JD Parsing | 3.1 JD Module + Epic 5 Skill Taxonomy |
| 3.3 Candidate Ranking | 3.2 JD Parsing + Epic 5 Skill Matcher |
| 3.4 Semantic Search | 3.2 JD Parsing |
| 3.5 JD Upload Frontend | 3.1, 3.2 |
| 3.6 Candidate Results | 3.3, 3.5 |
| 3.7 Search Frontend | 3.4, 3.5 |
