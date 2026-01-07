# Story 9.4: Job Recommendations

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Job Seeker,
I want to receive personalized job recommendations based on my CV analysis and profile,
So that I can discover relevant opportunities without manually searching and increase my chances of finding the perfect job match.

## Acceptance Criteria

### Backend Requirements

1. **Recommendation Algorithm** (Core Logic)
   - **Given** a Job Seeker has uploaded at least one CV with analysis completed, **When** they request job recommendations, **Then** system generates a ranked list of relevant jobs based on:
     - Skills extracted from their CV(s)
     - Experience level (min_experience_years matching)
     - Job preferences (if profile data available)
     - Semantic similarity between CV content and job descriptions
   - **Algorithm priorities:**
     1. Skills match score (primary weight: 40%)
     2. Experience level compatibility (30%)
     3. Location preference match (15%)
     4. Semantic similarity via vector search (15%)
   - **Minimum match threshold:** 60% overall score to appear in recommendations

2. **Recommendations Endpoint** (NEW)
   - **Given** an authenticated Job Seeker, **When** they request `GET /api/v1/jobs/recommendations`, **Then** system returns:
     - Top 10 recommended jobs sorted by match score (descending)
     - Each job includes: job details + `match_score` (0-100) + `match_reasons` (array of strings)
   - **Match reasons examples:**
     - "85% of your skills match this position"
     - "Your 3 years experience meets the requirements"
     - "Remote work preference matches"
   - **Caching strategy:** Cache recommendations for 1 hour per user to reduce computation
   - **Error cases:**
     - 401 if not authenticated
     - 404 if user has no CVs uploaded
     - 200 with empty array if no jobs meet threshold

3. **Recommendation Service Layer** (NEW)
   - **Method:** `get_recommendations_for_user(db, user_id, limit=10)`
   - **Logic flow:**
     1. Fetch user's most recent CV with analysis
     2. Extract skills, experience, preferences from CV analysis
     3. Query active jobs with vector similarity search on CV embedding
     4. Calculate match score for each candidate job
     5. Filter jobs >= 60% threshold
     6. Sort by match_score descending
     7. Return top N with match details
   - **Performance:** Query should complete in <2 seconds for typical dataset

### Frontend Requirements

4. **Recommendations Section** (Job Search Page Enhancement)
   - **Given** a Job Seeker navigates to `/jobs` page, **When** page loads, **Then** display:
     - Prominent "Recommended for You" section at the top (above search results)
     - Card grid showing top 6 recommended jobs
     - Each card shows: job title, company, location, match score badge, salary (if available)
     - "View All Recommendations" button linking to dedicated recommendations page
   - **Given** user has no CVs, **When** viewing recommendations section, **Then** show CTA card: "Upload your CV to get personalized recommendations" with upload button
   - **Given** user has CV but no recommendations found, **When** loading, **Then** show message: "No matches found yet. Try broadening your job search criteria."

5. **Dedicated Recommendations Page** (NEW: `/jobs/recommendations`)
   - **Given** a Job Seeker navigates to `/jobs/recommendations`, **When** page loads, **Then** display:
     - Full list of all recommended jobs (paginated, 20 per page)
     - Filter sidebar: Min match score slider (60-100%)
     - Sort options: "Best Match" (default), "Most Recent", "Highest Salary"
     - Each job card shows detailed match breakdown
   - **Match breakdown UI:**
     - Overall match score (circular progress indicator)
     - List of match reasons with icons
     - Skills matched vs required (e.g., "8/10 skills matched")
   - **SEO:** Meta title "Personalized Job Recommendations | Your Profile"

6. **Job Service Integration** (Enhancement)
   - **Add method:** `getRecommendations(limit?: number)`
   - **Add type:** `JobRecommendation` extending `JobDescriptionResponse` with:
     ```typescript
     interface JobRecommendation extends JobDescriptionResponse {
       match_score: number;        // 0-100
       match_reasons: string[];     // Human-readable match explanations
       skills_matched: number;      // Count of user skills matching job
       skills_required: number;     // Total skills required by job
     }
     ```
   - **Caching:** Implement SWR (stale-while-revalidate) for recommendations data

## Tasks / Subtasks

- [ ] Backend: Implement recommendation algorithm with match scoring (AC: #1)
  - [ ] Create `calculate_match_score()` function with 4-factor weighting
  - [ ] Implement skills matching logic (40% weight)
  - [ ] Implement experience level matching (30% weight)
  - [ ] Implement location preference matching (15% weight)
  - [ ] Integrate vector similarity search (15% weight)
  - [ ] Generate human-readable match reasons

- [ ] Backend: Create recommendations endpoint (AC: #2)
  - [ ] Add `GET /api/v1/jobs/recommendations` route in `router.py`
  - [ ] Implement query parameter validation (limit, min_score)
  - [ ] Add caching with 1-hour TTL
  - [ ] Handle error cases (401, 404, 500)
  - [ ] Add `JobRecommendationResponse` schema in `schemas.py`

- [ ] Backend: Implement recommendation service layer (AC: #3)
  - [ ] Create `get_recommendations_for_user()` in `services.py`
  - [ ] Fetch user's most recent CV with eager loading (selectinload)
  - [ ] Extract skills, experience from CV analysis
  - [ ] Query active jobs via vector similarity (top 50)
  - [ ] Apply match scoring algorithm to candidates
  - [ ] Filter by 60% threshold and sort by match score
  - [ ] Optimize for <2 second performance

- [ ] Frontend: Create RecommendationsSection component (AC: #4)
  - [ ] Create component in `features/jobs/components/RecommendationsSection.tsx`
  - [ ] Fetch top 6 recommendations on mount
  - [ ] Display horizontal scrollable card grid
  - [ ] Handle "no CV" state with CTA card
  - [ ] Handle "no recommendations" state with message
  - [ ] Add "View All" button linking to dedicated page

- [ ] Frontend: Create dedicated recommendations page (AC: #5)
  - [ ] Create page at `app/jobs/recommendations/page.tsx`
  - [ ] Implement SSR data fetching with auth check
  - [ ] Add filter sidebar (min match score slider)
  - [ ] Add sort options (Best Match, Most Recent, Highest Salary)
  - [ ] Display paginated job list (20 per page)
  - [ ] Add SEO metadata

- [ ] Frontend: Implement job service integration (AC: #6)
  - [ ] Add `getRecommendations()` method to `job.service.ts`
  - [ ] Define `JobRecommendation` interface in `@datn/shared-types`
  - [ ] Implement SWR caching strategy
  - [ ] Create RecommendationCard component with match score badge
  - [ ] Create MatchBreakdown component with visual indicators

- [ ] Integration & Testing
  - [ ] Integrate RecommendationsSection into `/jobs` page
  - [ ] Test all acceptance criteria scenarios
  - [ ] Verify algorithm accuracy with sample data
  - [ ] Performance test (<2 seconds for recommendations)
  - [ ] Test caching behavior
  - [ ] Test error handling and edge cases

## Dev Notes

### 🎯 Implementation Summary

**Status:** Ready for development

**Epic Context:** Story 9.4 builds on the foundation of Stories 9.1-9.3 (completed), adding intelligent job discovery powered by the existing CV analysis system from Epic 2.

### 📂 Expected Files to Create/Modify

#### Backend Files (NEW)
- `backend/app/modules/jobs/services.py` - Add `get_recommendations_for_user()` method
- `backend/app/modules/jobs/router.py` - Add `GET /api/v1/jobs/recommendations` endpoint
- `backend/app/modules/jobs/schemas.py` - Add `JobRecommendationResponse` schema with match details

#### Backend Files (MODIFY)
- `backend/app/modules/jobs/models.py` - Review if any model changes needed (likely none)
- `backend/app/core/vector_service.py` - May need to enhance vector similarity search for recommendations

#### Frontend Files (NEW)
- `frontend/app/jobs/recommendations/page.tsx` - Dedicated recommendations page
- `frontend/features/jobs/components/RecommendationsSection.tsx` - Section for main jobs page
- `frontend/features/jobs/components/RecommendationCard.tsx` - Job card with match details
- `frontend/features/jobs/components/MatchBreakdown.tsx` - Visual match score breakdown

#### Frontend Files (MODIFY)
- `frontend/app/jobs/page.tsx` - Integrate `<RecommendationsSection />` at top
- `frontend/services/job.service.ts` - Add `getRecommendations()` method
- `frontend/features/jobs/actions.ts` - Add Server Action for fetching recommendations (if needed)
- `packages/shared-types/src/job.ts` - Add `JobRecommendation` interface

### 🏗️ Architecture Compliance

#### Critical Fullstack Rules (Coding Standards)
✅ **HttpOnly Cookies:** Use Server Actions or SSR for initial data fetch - no client-side auth token access  
✅ **API Service Layer:** All API calls through `job.service.ts` - no direct fetch in components  
✅ **Type Sharing:** Define `JobRecommendation` in `@datn/shared-types` and import everywhere  
✅ **Backend Modularity:** New logic in `modules/jobs/services.py` following established pattern  
✅ **Protected Routes:** Recommendations page uses Layout Guard for Job Seeker role  

#### SQLAlchemy Async Rules
✅ **Eager Loading:** When fetching CV with analysis for recommendations, use `selectinload(CV.analysis)`  
✅ **Store Before Commit:** Not applicable (read-only operation for recommendations)  
✅ **Relationship Handling:** Load user's CVs and related analysis data eagerly to avoid lazy-load errors  
✅ **Pydantic Conversion:** Convert ORM results to `JobRecommendationResponse` schemas before returning  

#### Component Hierarchy
```
lib/hooks/                              [Could add: useRecommendations hook]
components/common/                      [Reuse: Badge, Progress, Card]
features/jobs/components/               [NEW: RecommendationsSection, RecommendationCard, MatchBreakdown]
app/jobs/recommendations/               [NEW: Dedicated recommendations page]
```

### 🧮 Recommendation Algorithm Details

#### Match Score Calculation (Pseudo-code)
```python
def calculate_match_score(user_cv_analysis, job_desc):
    """
    Calculate 0-100 match score based on multiple factors
    """
    # 1. Skills Match (40% weight)
    user_skills = set(user_cv_analysis.skills)  # From CV analysis
    job_skills = set(job_desc.required_skills)
    skills_match_ratio = len(user_skills & job_skills) / len(job_skills) if job_skills else 0
    skills_score = skills_match_ratio * 40
    
    # 2. Experience Match (30% weight)
    user_exp = user_cv_analysis.experience_years or 0
    required_exp = job_desc.min_experience_years or 0
    if user_exp >= required_exp:
        exp_score = 30  # Full score if meets requirements
    elif user_exp >= required_exp * 0.7:  # Within 70% is acceptable
        exp_score = 20
    else:
        exp_score = 0
    
    # 3. Location Preference (15% weight)
    # If user has location preference in profile
    user_location_pref = get_user_location_preference(user)  # e.g., "remote"
    location_score = 15 if job_desc.location_type == user_location_pref else 0
    
    # 4. Semantic Similarity via Vector Search (15% weight)
    cv_embedding = user_cv_analysis.embedding  # 768-dim vector
    jd_embedding = job_desc.embedding
    cosine_sim = cosine_similarity(cv_embedding, jd_embedding)  # 0-1
    semantic_score = cosine_sim * 15
    
    total_score = skills_score + exp_score + location_score + semantic_score
    
    # Generate match reasons
    reasons = []
    if skills_match_ratio >= 0.8:
        reasons.append(f"{int(skills_match_ratio*100)}% of your skills match this position")
    if user_exp >= required_exp:
        reasons.append(f"Your {user_exp} years experience meets the requirements")
    if location_score > 0:
        reasons.append(f"{user_location_pref.capitalize()} work preference matches")
    if cosine_sim >= 0.7:
        reasons.append("Strong semantic match with your CV content")
    
    return {
        "match_score": int(total_score),
        "match_reasons": reasons,
        "skills_matched": len(user_skills & job_skills),
        "skills_required": len(job_skills)
    }
```

#### Vector Search Strategy
- Use existing `pgvector` infrastructure (already set up for semantic candidate search in Epic 3)
- Query: `SELECT * FROM job_descriptions WHERE embedding <=> user_cv_embedding ORDER BY distance LIMIT 50`
- Then apply full match scoring algorithm to top 50 candidates
- This hybrid approach (vector + rule-based) ensures both semantic and explicit requirement matching

### 🔌 API Endpoints

#### GET /api/v1/jobs/recommendations
**Purpose:** Fetch personalized job recommendations  
**Auth:** Required (Job Seeker role)  
**Query Parameters:**
- `limit` (optional, default=10): Max number of recommendations to return
- `min_score` (optional, default=60): Minimum match score threshold

**Response:**
```typescript
{
  recommendations: [
    {
      // All fields from JobDescriptionResponse
      id: string;
      title: string;
      description: string;
      required_skills: string[];
      min_experience_years: number | null;
      location_type: "remote" | "hybrid" | "on-site";
      salary_min: number | null;
      salary_max: number | null;
      job_type: "full-time" | "part-time" | "contract" | "internship" | "freelance" | null;
      benefits: string[];
      is_active: boolean;
      uploaded_at: string;
      
      // NEW: Recommendation-specific fields
      match_score: number;           // 0-100
      match_reasons: string[];        // ["85% skills match", "Experience meets requirements"]
      skills_matched: number;         // e.g., 8
      skills_required: number;        // e.g., 10
    }
  ],
  total: number;        // Total recommendations before pagination
  user_cv_id: string;   // CV used for generating recommendations
}
```

**Error Responses:**
- `401 Unauthorized` - User not authenticated
- `404 Not Found` - User has no CVs or CV analysis incomplete
- `500 Internal Server Error` - Recommendation engine failure

### 🎨 Frontend Components

#### RecommendationsSection Component
**Location:** `frontend/features/jobs/components/RecommendationsSection.tsx`

**Features:**
- Fetches top 6 recommendations on mount
- Displays horizontal scrollable card grid
- Shows loading skeleton while fetching
- Handles "no CV" state with CTA card
- Handles "no recommendations" state with helpful message
- "View All" button navigates to dedicated page

**State Management:**
- `recommendations` - Array of recommendation data
- `loading` - Loading state
- `error` - Error state (if fetch fails)

#### RecommendationCard Component
**Location:** `frontend/features/jobs/components/RecommendationCard.tsx`

**Props:**
```typescript
interface RecommendationCardProps {
  job: JobRecommendation;
  onApply?: (jobId: string) => void;  // Optional apply handler
  variant?: 'compact' | 'detailed';    // Display mode
}
```

**Features:**
- Match score badge (color-coded: green 80+, yellow 70-79, blue 60-69)
- Job title, company info (if available), location
- Salary range (if provided)
- Quick apply button
- "View Details" link to job detail page (`/jobs/[id]`)
- Hover effect with match reasons preview

**Compact variant (for main jobs page):**
- Card size: ~300x200px
- Shows top 2 match reasons
- Minimal styling

**Detailed variant (for recommendations page):**
- Full card with all match reasons
- Skills matched indicator (e.g., "8/10 skills")
- Expandable description preview

#### MatchBreakdown Component
**Location:** `frontend/features/jobs/components/MatchBreakdown.tsx`

**Purpose:** Visual representation of match score and factors

**Features:**
- Circular progress indicator for overall score
- Breakdown of match factors:
  - Skills: X/Y matched (progress bar)
  - Experience: ✓ or ✗ with explanation
  - Location: ✓ or ✗
  - Semantic similarity: High/Medium/Low
- Color-coded sections (green = strong, yellow = moderate, gray = weak)

### 🧪 Testing Considerations

**Manual Testing Checklist:**
- [ ] User with CV can view recommendations on `/jobs` page
- [ ] User without CV sees "Upload CV" CTA instead of recommendations
- [ ] Match score accurately reflects CV-job alignment
- [ ] Match reasons are human-readable and accurate
- [ ] "View All" button navigates to `/jobs/recommendations`
- [ ] Recommendations page shows full list with pagination
- [ ] Min match score filter works correctly
- [ ] Sorting options work (Best Match, Most Recent, Salary)
- [ ] Quick apply from recommendation card opens apply dialog
- [ ] Caching: Repeated requests within 1 hour use cached data
- [ ] Error handling: Graceful display if recommendation engine fails

**Backend Testing:**
- [ ] Recommendation algorithm produces sensible scores
- [ ] Vector similarity search returns relevant jobs
- [ ] Skills matching logic handles partial matches
- [ ] Experience level filtering works correctly
- [ ] API returns 404 if user has no CVs
- [ ] API respects `limit` and `min_score` query parameters
- [ ] Performance: Recommendation generation completes in <2 seconds

### 📝 Code Patterns to Follow

#### Server-Side Recommendations Fetch (SSR)
```typescript
// frontend/app/jobs/recommendations/page.tsx
export default async function RecommendationsPage() {
  const session = await getSession();
  if (!session) redirect("/login");
  
  // Fetch recommendations server-side
  const recommendations = await jobService.getRecommendations();
  
  return <RecommendationsPageClient recommendations={recommendations} />;
}
```

#### Service Layer Pattern
```typescript
// frontend/services/job.service.ts
async getRecommendations(limit = 10, minScore = 60): Promise<JobRecommendation[]> {
  const response = await apiClient.get('/jobs/recommendations', {
    params: { limit, min_score: minScore },
  });
  return response.data.recommendations;
}
```

#### Backend Service Pattern
```python
# backend/app/modules/jobs/services.py
async def get_recommendations_for_user(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    min_score: int = 60
) -> list[JobRecommendationResponse]:
    """
    Generate personalized job recommendations for a user based on their CV.
    
    Args:
        db: Database session
        user_id: User ID to generate recommendations for
        limit: Maximum number of recommendations to return
        min_score: Minimum match score threshold (0-100)
    
    Returns:
        List of job recommendations with match scores and reasons
    
    Raises:
        HTTPException 404: If user has no CVs or CV analysis incomplete
    """
    # 1. Get user's most recent CV with analysis (eager load)
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analysis))  # Eager load analysis
        .where(CV.user_id == user_id)
        .order_by(CV.uploaded_at.desc())
        .limit(1)
    )
    user_cv = result.scalar_one_or_none()
    
    if not user_cv or not user_cv.analysis:
        raise HTTPException(
            status_code=404,
            detail="No CV analysis found. Please upload and analyze a CV first."
        )
    
    # 2. Extract skills and experience from CV analysis
    cv_analysis = user_cv.analysis
    user_skills = set(cv_analysis.skills or [])
    user_experience = cv_analysis.experience_years or 0
    cv_embedding = cv_analysis.embedding
    
    # 3. Get candidate jobs via vector similarity search
    # Query top 50 jobs by semantic similarity, then apply detailed scoring
    candidate_jobs = await vector_search_similar_jobs(
        db=db,
        embedding=cv_embedding,
        limit=50,
        only_active=True
    )
    
    # 4. Calculate match score for each candidate
    recommendations = []
    for job in candidate_jobs:
        match_details = calculate_match_score(
            user_skills=user_skills,
            user_experience=user_experience,
            job=job
        )
        
        if match_details["match_score"] >= min_score:
            recommendations.append(
                JobRecommendationResponse(
                    **job.dict(),  # All job fields
                    **match_details  # Match score, reasons, skills counts
                )
            )
    
    # 5. Sort by match score descending and limit
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:limit]


def calculate_match_score(
    user_skills: set[str],
    user_experience: int,
    job: JobDescription
) -> dict:
    """
    Calculate match score and generate match reasons.
    
    Returns:
        {
            "match_score": int (0-100),
            "match_reasons": list[str],
            "skills_matched": int,
            "skills_required": int
        }
    """
    # Implementation as shown in Algorithm Details section above
    pass
```

### 🔗 Related Stories & Dependencies

**Dependencies (Completed):**
- ✅ Story 1.1-1.3: User authentication and profile (Epic 1)
- ✅ Story 2.1-2.3: CV upload and analysis (Epic 2) - **CRITICAL DEPENDENCY**
- ✅ Story 3.4: Semantic candidate search infrastructure (Epic 3) - Vector search foundation
- ✅ Story 9.1: Basic job search (Epic 9)
- ✅ Story 9.3: Job application flow (Epic 9)

**Enables (Future):**
- Future Story: Email notifications for new recommended jobs
- Future Story: User feedback on recommendations (thumbs up/down) to improve algorithm
- Future Story: Job alerts based on saved recommendation criteria

### ⚠️ Known Issues & Technical Debt

**Current Limitations:**
1. **No User Preference Storage:** Recommendations based purely on CV data, not on explicit user preferences (e.g., industry, company size, remote-only)
2. **No Historical Data:** Algorithm doesn't learn from user's past applications or job views
3. **No Collaborative Filtering:** Doesn't consider "users like you also applied to..." patterns
4. **Static Algorithm:** Match score weights are hardcoded, not ML-based
5. **No Real-time Updates:** Recommendations cached for 1 hour, may miss very fresh job postings

**Performance Considerations:**
- Recommendation calculation is compute-intensive (vector search + scoring for 50+ jobs)
- Consider background job to pre-compute recommendations for all users nightly
- For high-traffic scenarios, implement Redis caching with longer TTL

**Security Considerations:**
- Ensure user can only access their own recommendations (validate user_id in endpoint)
- Sanitize match_reasons text to prevent injection if using user-generated data

### 🚀 Future Enhancements (Recommendations for Next Stories)

1. **Story 9.4.1: User Preference Management** (Job Seeker)
   - Allow users to set explicit job preferences (industries, company size, remote-only, salary range)
   - Integrate preferences into recommendation algorithm (add 10% weight for preference match)
   - UI: Settings page with preference form

2. **Story 9.4.2: Recommendation Feedback Loop** (ML Enhancement)
   - Add "Not Interested" / "Interested" buttons on recommendation cards
   - Track user interactions (views, applications, dismissals)
   - Use feedback to retrain/tune recommendation weights
   - Consider ML model (e.g., matrix factorization or neural collaborative filtering)

3. **Story 9.4.3: Job Alerts** (Notification System)
   - Allow users to subscribe to recommendation alerts
   - Send email digest of new recommendations (daily or weekly)
   - In-app notification bell for new recommendations
   - Integration with Epic 7 (Real-time Messaging) for push notifications

4. **Story 9.4.4: Recommendation Explanations** (Transparency)
   - Detailed breakdown page explaining why each job was recommended
   - Visualize algorithm factors (pie chart of score components)
   - Show how user's CV aligns with job requirements (side-by-side comparison)

### 📚 References

- [Source: _bmad-output/planning-artifacts/architecture/coding-standards.md#Critical Fullstack Rules]
- [Source: _bmad-output/planning-artifacts/architecture/coding-standards.md#SQLAlchemy Async Rules]
- [Source: _bmad-output/planning-artifacts/architecture/database-schema.md#CVs and Analysis Tables]
- [Source: _bmad-output/planning-artifacts/architecture/database-schema.md#Job Descriptions Table]
- [Source: _bmad-output/planning-artifacts/architecture/api-specification.md#Job Endpoints]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 9: Advanced Job Search Application]
- [Source: _bmad-output/planning-artifacts/prd.md#Product Scope - Tìm kiếm & Ứng tuyển Nâng cao]
- [Source: _bmad-output/implementation-artifacts/9-3-job-application-flow.md#Related Stories & Dependencies]

### 🎓 Learning from Previous Stories

**From Story 9.3 (Job Application Flow):**
- ✅ **Pattern:** Use Server Actions for data fetching with auth
- ✅ **Pattern:** Modal/Dialog pattern for user actions (ApplyJobDialog) - consider similar for "Save Recommendation"
- ✅ **Pattern:** Service layer centralization (`job.service.ts`)
- ✅ **Pattern:** SSR for initial page load with client-side interactivity
- ⚠️ **Avoid:** Don't access `document.cookie` in client components
- ⚠️ **Avoid:** Don't make direct API calls from components

**From Story 3.4 (Semantic Candidate Search):**
- ✅ **Reuse:** Vector similarity search logic already implemented
- ✅ **Reuse:** `pgvector` infrastructure for embeddings
- ✅ **Pattern:** Hybrid search (vector + filters) for best results
- 🔄 **Adapt:** Reverse the direction - instead of "find candidates for job", we're "finding jobs for candidate"

**From Story 2.3 (CV Analysis Results Display):**
- ✅ **Reuse:** CV analysis data structure (skills, experience_years)
- ✅ **Pattern:** Display AI-generated insights in user-friendly format
- 🔄 **Adapt:** Use similar visualization patterns for match breakdown

---

## Dev Agent Record

### Agent Model Used
(To be filled by Dev agent when working on this story)

### Debug Log References
(To be filled during implementation)

### Completion Notes List
(To be added as story progresses)

### File List
(To be updated with actual files created/modified during implementation)
