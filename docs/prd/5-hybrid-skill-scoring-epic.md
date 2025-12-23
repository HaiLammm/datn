# Epic 5: Hybrid Skill Scoring Enhancement

## 5.1. Goals and Background Context

### 5.1.1. Goals

- Cải thiện độ chính xác và nhất quán của việc chấm điểm kỹ năng (skill scoring) trong CV
- Triển khai hệ thống hybrid kết hợp rule-based extraction với LLM analysis
- Cung cấp skill breakdown chi tiết giúp ứng viên hiểu rõ điểm mạnh/yếu
- Chuẩn hóa skill extraction với taxonomy theo ngành IT
- Gợi ý các kỹ năng hot/in-demand cho ứng viên
- Hỗ trợ so khớp skill với Job Description (skill matching)

### 5.1.2. Background Context

Hệ thống CV analysis hiện tại sử dụng 100% LLM để chấm điểm skill (0-25 điểm). Phương pháp này có các hạn chế:

| Vấn đề | Mô tả |
|--------|-------|
| **Thiếu nhất quán** | Cùng một CV có thể nhận điểm khác nhau giữa các lần chấm |
| **Không chuẩn hóa** | "ReactJS", "React.js", "react" được coi là khác nhau |
| **Thiếu transparency** | User không biết tại sao nhận điểm như vậy |
| **Không có skill matching** | Chưa so khớp với yêu cầu JD |

Giải pháp Hybrid Skill Scoring sẽ kết hợp:
- **Rule-based extraction** (75%): Chuẩn hóa, phân loại, đếm skill
- **LLM analysis** (25%): Đánh giá evidence, context của skill trong CV

### 5.1.3. Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-12-16 | 0.1.0 | Initial PRD draft for Hybrid Skill Scoring | John (PM) |

---

## 5.2. Requirements

### 5.2.1. Functional Requirements

| ID | Requirement |
|----|-------------|
| **FR-SS1** | Hệ thống phải trích xuất skills từ CV sử dụng rule-based pattern matching |
| **FR-SS2** | Hệ thống phải chuẩn hóa skill names theo taxonomy chuẩn (ví dụ: "ReactJS" → "react") |
| **FR-SS3** | Hệ thống phải phân loại skills theo categories: programming_languages, frameworks, databases, devops, soft_skills |
| **FR-SS4** | Hệ thống phải tính điểm Completeness (0-7) dựa trên số lượng và đa dạng skills |
| **FR-SS5** | Hệ thống phải tính điểm Categorization (0-6) dựa trên cách tổ chức skills trong CV |
| **FR-SS6** | Hệ thống phải tính điểm Evidence (0-6) từ LLM đánh giá skill được chứng minh trong experience |
| **FR-SS7** | Hệ thống phải tính điểm Market Relevance (0-6) dựa trên hot skills của ngành |
| **FR-SS8** | Hệ thống phải trả về skill_breakdown chi tiết trong API response |
| **FR-SS9** | Hệ thống phải gợi ý các skills cần học (skill_recommendations) cho ứng viên |
| **FR-SS10** | Hệ thống phải hỗ trợ so khớp skills của CV với requirements trong JD |
| **FR-SS11** | Hệ thống phải tính skill_match_rate khi so khớp CV với JD |
| **FR-SS12** | Hệ thống phải liệt kê matched_skills, missing_skills, extra_skills khi so khớp |

### 5.2.2. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| **NFR-SS1** | Skill taxonomy phải dễ dàng mở rộng và cập nhật |
| **NFR-SS2** | Độ chính xác skill extraction phải đạt mức chấp nhận được cho IT skills |
| **NFR-SS3** | API response schema changes phải backward compatible với soft deprecation |
| **NFR-SS4** | Skill scoring phải deterministic cho rule-based components |
| **NFR-SS5** | System phải log skill extraction results cho debugging và improvement |

> **Note:** Đây là giai đoạn demo, các yêu cầu về performance timing đã được loại bỏ. Focus vào tính năng hoạt động đúng.

### 5.2.3. Compatibility Requirements

| ID | Requirement |
|----|-------------|
| **CR-SS1** | Thêm columns mới vào `cv_analyses` table mà không break existing data |
| **CR-SS2** | Mở rộng API response schema với backward compatibility |
| **CR-SS3** | Tích hợp với existing RAG service cho career field detection |
| **CR-SS4** | Hoạt động với existing LLM (Ollama llama3.1:8b) |

---

## 5.3. User Interface Enhancement Goals

### 5.3.1. UI Changes Required

Thêm section mới hiển thị skill breakdown chi tiết trong trang CV Analysis Result.

| Screen | Changes |
|--------|---------|
| **CV Analysis Result** | Thêm "Skill Analysis" section với breakdown chart |
| **Skill Breakdown** | Hiển thị 4 sub-scores: Completeness, Categorization, Evidence, Market Relevance |
| **Extracted Skills** | Hiển thị skills theo categories với badges |
| **Recommendations** | Hiển thị danh sách skills gợi ý học thêm |

### 5.3.2. Mockup Concept

```
┌─────────────────────────────────────────────────────────────┐
│ Skill Analysis                                    Score: 21/25 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Breakdown:                                              │ │
│ │  Completeness      ████████░░  7/7                      │ │
│ │  Categorization    █████░░░░░  5/6                      │ │
│ │  Evidence          ████░░░░░░  4/6                      │ │
│ │  Market Relevance  █████░░░░░  5/6                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Extracted Skills (15 skills found):                     │ │
│ │                                                         │ │
│ │ Programming:  [Python] [JavaScript] [TypeScript]        │ │
│ │ Frameworks:   [React] [FastAPI] [Next.js]               │ │
│ │ Databases:    [PostgreSQL] [Redis] [MongoDB]            │ │
│ │ DevOps:       [Docker] [AWS] [CI/CD]                    │ │
│ │ Soft Skills:  [Teamwork] [Communication] [Leadership]   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Recommendations:                                        │ │
│ │ - Consider learning Kubernetes - hot skill in 2024      │ │
│ │ - Add proficiency levels to your skills                 │ │
│ │ - Include more evidence of skill usage in experience    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.4. Technical Assumptions

### 5.4.1. Database Changes

```sql
-- Thêm columns vào cv_analyses table
ALTER TABLE cv_analyses ADD COLUMN skill_breakdown JSONB;
ALTER TABLE cv_analyses ADD COLUMN skill_categories JSONB;
ALTER TABLE cv_analyses ADD COLUMN skill_recommendations TEXT[];

-- skill_breakdown format:
-- {
--   "completeness_score": 7,
--   "categorization_score": 5,
--   "evidence_score": 4,
--   "market_relevance_score": 5,
--   "total_score": 21
-- }

-- skill_categories format:
-- {
--   "programming_languages": ["python", "javascript"],
--   "frameworks": ["react", "fastapi"],
--   ...
-- }
```

### 5.4.2. API Response Schema Changes

```python
# Mở rộng AnalysisResult schema
class SkillBreakdown(BaseModel):
    completeness_score: int  # 0-7
    categorization_score: int  # 0-6
    evidence_score: int  # 0-6
    market_relevance_score: int  # 0-6
    total_score: int  # 0-25

class SkillCategories(BaseModel):
    programming_languages: list[str]
    frameworks: list[str]
    databases: list[str]
    devops: list[str]
    soft_skills: list[str]
    other: list[str]

class AnalysisResult(BaseModel):
    # Existing fields...
    ai_score: int
    ai_summary: str
    extracted_skills: list[str]  # Deprecated, use skill_categories
    
    # New fields
    skill_breakdown: SkillBreakdown
    skill_categories: SkillCategories
    skill_recommendations: list[str]
```

### 5.4.3. New Files Structure

```
backend/app/modules/ai/
├── skill_taxonomy.py      # NEW: Skill definitions & hot skills
├── skill_extractor.py     # NEW: Rule-based extraction
├── skill_scorer.py        # NEW: Hybrid scoring engine
├── service.py             # UPDATE: Integrate skill scorer
├── schemas.py             # UPDATE: Add new schemas
└── models.py              # UPDATE: Add new columns
```

### 5.4.4. Skill Taxonomy Scope (IT Focus)

| Category | Sample Skills |
|----------|---------------|
| **Programming Languages** | Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby |
| **Frameworks** | React, Vue, Angular, FastAPI, Django, Spring, Next.js, Express |
| **Databases** | PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, SQLite |
| **DevOps** | Docker, Kubernetes, AWS, GCP, Azure, CI/CD, Terraform, Ansible |
| **Soft Skills** | Communication, Teamwork, Leadership, Problem Solving, Agile |

**Hot Skills 2024 (IT):** Python, React, TypeScript, Docker, Kubernetes, AWS, AI/ML, Go

---

## 5.5. User Stories

### Story 5.1: Skill Taxonomy & Extractor Foundation

**As a** system,
**I want** a skill taxonomy and rule-based extractor,
**So that** skills can be extracted and normalized consistently.

#### Acceptance Criteria

1. Tạo file `skill_taxonomy.py` với IT skill definitions
2. Skill taxonomy bao gồm 5 categories: programming_languages, frameworks, databases, devops, soft_skills
3. Mỗi skill có canonical name và list of aliases (ví dụ: "react" → ["reactjs", "react.js"])
4. Tạo HOT_SKILLS_2024 dict cho IT ngành
5. Tạo file `skill_extractor.py` với class SkillExtractor
6. SkillExtractor.extract_skills() trả về Dict[category, List[skill]]
7. SkillExtractor.normalize_skill() chuẩn hóa skill name
8. Basic tests cho skill extraction

---

### Story 5.2: Hybrid Skill Scorer Implementation

**As a** system,
**I want** a hybrid skill scorer combining rule-based and LLM analysis,
**So that** skill scores are accurate, consistent, and explainable.

#### Acceptance Criteria

1. Tạo file `skill_scorer.py` với class SkillScorer
2. Implement `_calculate_completeness()` trả về 0-7 điểm
3. Implement `_calculate_categorization()` trả về 0-6 điểm
4. Implement `_calculate_market_relevance()` trả về 0-6 điểm
5. Evidence score (0-6) được extract từ LLM response
6. `calculate_skill_score()` trả về full breakdown + recommendations
7. Recommendations được generate dựa trên gaps phát hiện
8. Scoring deterministic cho rule-based components (same input → same output)

---

### Story 5.3: Database Schema & API Response Update

**As a** developer,
**I want** updated database schema and API response,
**So that** skill breakdown data is persisted and returned to clients.

#### Acceptance Criteria

1. Tạo Alembic migration thêm columns: skill_breakdown, skill_categories, skill_recommendations
2. Columns sử dụng JSONB type cho flexibility
3. Update `CVAnalysis` model với new columns
4. Update `AnalysisResult` schema với SkillBreakdown, SkillCategories
5. Backward compatibility: existing `extracted_skills` field vẫn hoạt động
6. Migration có thể rollback safely

---

### Story 5.4: AI Service Integration

**As a** system,
**I want** skill scorer integrated into AI service,
**So that** CV analysis uses hybrid skill scoring automatically.

#### Acceptance Criteria

1. Update `AIService.__init__()` để khởi tạo SkillScorer
2. Update `_perform_ai_analysis()` để gọi skill scorer
3. Extract evidence score từ LLM response
4. Merge skill_breakdown vào analysis results
5. Update `_save_analysis_results()` để save new columns
6. Existing CV analysis flow không bị break
7. Logging skill extraction và scoring results

---

### Story 5.5: Skill-JD Matching Foundation

**As a** recruiter,
**I want** to see skill matching between CV and JD,
**So that** I can evaluate candidate fit quickly.

#### Acceptance Criteria

1. Implement `SkillMatcher` class trong `skill_scorer.py`
2. `match_skills(cv_skills, jd_requirements)` trả về match result
3. Match result bao gồm: matched_skills, missing_skills, extra_skills
4. Tính `skill_match_rate` (0.0 - 1.0)
5. Skill matching sử dụng normalized skill names
6. API endpoint `/api/v1/cvs/{id}/match` nhận JD text và trả về match result

---

### Story 5.6: Frontend Skill Breakdown UI

**As a** job seeker,
**I want** to see detailed skill breakdown in my CV analysis,
**So that** I understand my strengths and areas for improvement.

#### Acceptance Criteria

1. Tạo `SkillBreakdownCard` component
2. Hiển thị 4 sub-scores với progress bars
3. Tạo `SkillCategoriesDisplay` component với skill badges
4. Skill badges color-coded theo category
5. Tạo `SkillRecommendations` component
6. Integrate vào CV analysis result page
7. Responsive design cho mobile

---

### Story 5.7: Enhanced Scoring and Job Match Score

**As a** Recruiter,
**I want** to see a specific "Job Match Score" for each candidate that prioritizes relevance to my Job Description,
**So that** I can quickly identify the most relevant applicants, independent of their "general" CV quality.

**As a** System,
**I want** the general skill scoring to be more nuanced,
**So that** I can account for the changing value of technologies over time and better evaluate senior candidates.

#### Acceptance Criteria

##### Backend
1. The `skill_taxonomy.py` file is updated to include a versioned dictionary for "hot skills" (e.g., `HOT_SKILLS_2023`, `HOT_SKILLS_2024`) with a `HOT_SKILLS_VERSIONS` mapping.
2. The `_calculate_market_relevance` method in `skill_scorer.py` is updated to check a skill against multiple years of hot skill lists (additive - skill is "hot" if in any checked year).
3. The LLM prompt for CV analysis is enhanced to give more weight to leadership roles and years of experience.
4. A new endpoint `POST /api/v1/jobs/{job_id}/match` is created that takes a CV ID and returns a specific job match score.
5. The "Job Match Score" calculation prioritizes skills listed in the JD over general "hot skills".

##### Frontend
6. The "Candidate Results" page (`/jobs/jd/[jdId]/candidates`) displays the new "Job Match Score" for each candidate.
7. The "Job Match Score" is displayed prominently on the `CandidateCard` component with clear color-coding (Green >= 70, Yellow >= 40, Red < 40).
8. The UI gracefully handles cases where the match score has not yet been calculated (loading/null state).

##### Testing
9. Unit and integration tests are created for the new backend logic (versioned hot skills, job match endpoint).
10. Frontend component tests are updated to verify the display of the new "Job Match Score".
11. E2E tests validate the end-to-end flow of viewing matched candidates with their job-specific scores.

#### Technical Notes

**New Data Structures:**
```python
# In skill_taxonomy.py
HOT_SKILLS_2023: Dict[str, List[str]] = {
    "programming_languages": ["python", "typescript", "go"],
    "frameworks": ["react", "nextjs", "fastapi"],
    # ... other categories
}

HOT_SKILLS_VERSIONS: Dict[int, Dict[str, List[str]]] = {
    2023: HOT_SKILLS_2023,
    2024: HOT_SKILLS_2024,
}
```

**New API Endpoint:**
```
POST /api/v1/jobs/{job_id}/match
Request Body: { "cv_id": "uuid-string" }
Response: {
    "cv_id": "string",
    "job_id": "string",
    "job_match_score": 88  // 0-100
}
```

**Rationale:** This endpoint differs from the existing `/api/v1/ai/cvs/{cv_id}/match` (Story 5.5) by:
- Being job-centric (job_id in path) rather than CV-centric
- Returning a single numeric score optimized for ranking display
- Using JD's parsed requirements rather than raw JD text

---

### Story 5.8: Fix Experience Years Extraction and Enhance Display

**As a** Recruiter,
**I want** to see clear experience comparison between candidate's years of experience and job requirements,
**So that** I can quickly assess if candidates meet experience requirements.

**As a** System,
**I want** to correctly extract experience years from CV analysis data,
**So that** experience scoring is accurate and not always zero/undefined.

#### Acceptance Criteria

##### Backend - Bug Fix
1. The `_extract_experience_years()` method in `candidate_ranker.py` correctly extracts from `ai_feedback["experience_breakdown"]["total_years"]`.
2. The `calculate_job_match_score()` function in `services.py` uses the same correct extraction path.
3. Experience score calculation handles all edge cases (has requirement, no requirement, no CV data).

##### Backend - API Enhancement
4. The `MatchBreakdownResponse` schema includes `required_experience_years` field.
5. API functions return the JD's required experience years in the breakdown response.

##### Frontend - Enhanced Display
6. Experience display shows comparison format: "X/Y năm (yêu cầu Y năm)" when JD has requirement.
7. Color-coding applied to experience display (green/yellow/red based on ratio).

##### Testing
8. Unit tests verify correct experience extraction from nested path.
9. Integration tests verify experience score calculation scenarios.
10. Frontend component tests verify experience comparison display.

#### Technical Notes

**Root Cause:** Experience extraction looks in wrong locations:
- **Bug:** `skill_breakdown["experience_years"]` and `ai_feedback["experience_years"]`
- **Fix:** `ai_feedback["experience_breakdown"]["total_years"]`

**UI Enhancement:**
```
BEFORE: "Kinh nghiệm: Không xác định" (always due to bug)
AFTER:  "Kinh nghiệm: 3/5 năm (yêu cầu 5 năm)" with color-coding
```

---

## 5.6. Implementation Priority

| Priority | Story | Rationale |
|----------|-------|-----------|
| **P0 - Must Have** | 5.1 Skill Taxonomy & Extractor | Nền tảng cho tất cả stories khác |
| **P0 - Must Have** | 5.2 Hybrid Skill Scorer | Core business logic |
| **P1 - Should Have** | 5.3 Database & API Update | Persistence và API contract |
| **P1 - Should Have** | 5.4 AI Service Integration | End-to-end integration |
| **P0 - Must Have** | 5.5 Skill-JD Matching | Advanced feature |
| **P2 - Nice to Have** | 5.6 Frontend UI | User-facing feature |
| **P1 - Should Have** | 5.7 Enhanced Scoring & Job Match Score | Recruiter-facing job match feature |
| **P0 - Must Have** | 5.8 Fix Experience Extraction & Display | Critical bug fix - experience scoring broken |

> **Demo Phase Note:** Focus vào P0 và P1 stories trước. P2 có thể defer nếu cần.

---

## 5.7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Skill taxonomy incomplete | Medium | High | Start với top 100 IT skills, iterate |
| LLM evidence scoring inconsistent | Medium | Medium | Weight LLM only 25% of total |
| Migration breaks existing data | High | Low | Test migration on staging first |
| Frontend integration delay | Medium | Low | Backend-first approach, UI can follow |

---

## 5.8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Skill extraction accuracy | Acceptable for demo | Manual review of sample CVs |
| Scoring consistency | Same CV → Same score (rule-based) | Test same CV multiple times |
| Feature completeness | P0 + P1 stories done | Story acceptance criteria met |

---

## 5.9. Dependencies

| Story | Depends On |
|-------|------------|
| 5.2 Hybrid Skill Scorer | 5.1 Skill Taxonomy |
| 5.3 Database & API | 5.2 Skill Scorer |
| 5.4 AI Service Integration | 5.2, 5.3 |
| 5.5 Skill-JD Matching | 5.1, 5.2 |
| 5.6 Frontend UI | 5.3, 5.4 |
| 5.7 Enhanced Scoring & Job Match | 5.1, 5.2, 5.5 |
| 5.8 Fix Experience Extraction | 5.7 (fixes bug in 5.7 implementation) |
