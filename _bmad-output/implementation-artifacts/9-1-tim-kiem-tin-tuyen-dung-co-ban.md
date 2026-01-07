# Story 9.1: Tìm kiếm tin tuyển dụng cơ bản

## Status
ready-for-dev

## Story
**As a** Job Seeker (Người tìm việc),
**I want** tìm kiếm tin tuyển dụng theo từ khóa và địa điểm,
**So that** tôi có thể nhanh chóng tìm thấy các cơ hội phù hợp với kỹ năng và vị trí địa lý mong muốn của mình.

## Acceptance Criteria

### AC1: Basic Search Interface
**Given** I am a logged-in Job Seeker,
**When** I navigate to the job search page (`/jobs/search`),
**Then** I see a search interface with:
- A text input field for "Keyword" (placeholder: "e.g., Python Developer, Data Scientist")
- A text input field for "Location" (placeholder: "e.g., Hà Nội, Hồ Chí Minh, Remote")
- A "Search" button
- An empty state message if no search has been performed yet

### AC2: Keyword Search
**Given** I am on the job search page,
**When** I enter a keyword (e.g., "Python Developer") and click "Search",
**Then** the system searches for job descriptions where the `title` OR `description` fields contain the keyword (case-insensitive),
**And** displays a list of matching job postings with:
- Job title
- Company name (recruiter email for MVP)
- Location type (remote/hybrid/on-site)
- Posted date (relative: "2 days ago")
- Brief description snippet (first 150 characters)

### AC3: Location Filter
**Given** I am on the job search page,
**When** I enter a location (e.g., "Hà Nội") and click "Search",
**Then** the system filters job descriptions where `location_type` matches the input (exact match for "remote", "hybrid", "on-site"),
**And** displays matching results sorted by `uploaded_at` DESC (newest first).

### AC4: Combined Search
**Given** I am on the job search page,
**When** I enter both keyword AND location and click "Search",
**Then** the system returns jobs that match BOTH criteria:
- Keyword match in `title` OR `description` (ILIKE)
- Location type matches input
**And** displays results sorted by relevance (newest first for MVP).

### AC5: Empty Results Handling
**Given** I have performed a search,
**When** no job descriptions match my search criteria,
**Then** the system displays a friendly message:
- "Không tìm thấy tin tuyển dụng nào phù hợp với tiêu chí của bạn."
- "Thử điều chỉnh từ khóa hoặc mở rộng phạm vi địa điểm."

### AC6: Pagination
**Given** search results contain more than 10 jobs,
**When** I view the results page,
**Then** the system displays:
- Maximum 10 job cards per page
- Pagination controls at the bottom (Previous/Next buttons + page numbers)
- Total results count (e.g., "Showing 1-10 of 47 results")

### AC7: Loading States
**Given** I have submitted a search,
**When** the system is fetching results,
**Then** I see a loading indicator (skeleton cards or spinner),
**And** the search button is disabled until results are loaded.

### AC8: Error Handling
**Given** I perform a search,
**When** the backend API fails or times out,
**Then** the system displays an error toast:
- "Đã xảy ra lỗi khi tìm kiếm. Vui lòng thử lại sau."
**And** allows me to retry the search.

## Tasks / Subtasks

### Backend Implementation

- [ ] **Task 1: Database Schema Verification (AC: 1-4)**
    - [ ] Verify `job_descriptions` table has required columns:
        - `id` (UUID, primary key)
        - `user_id` (UUID, FK to users)
        - `title` (VARCHAR(255), NOT NULL)
        - `description` (TEXT, NOT NULL)
        - `location_type` (VARCHAR(50), CHECK IN ('remote', 'hybrid', 'on-site'))
        - `uploaded_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
        - `is_active` (BOOLEAN, DEFAULT TRUE)
        - `required_skills` (TEXT[] - for future filtering)
    - [ ] Add index on `title` and `description` for faster ILIKE searches:
        ```sql
        CREATE INDEX idx_job_descriptions_search ON job_descriptions USING gin(to_tsvector('english', title || ' ' || description));
        ```
    - [ ] Add index on `location_type` for location filtering
    - [ ] Add index on `uploaded_at DESC` for sorting

- [ ] **Task 2: Pydantic Schemas (AC: All)**
    - [ ] In `backend/app/modules/jobs/schemas.py`, create:
        ```python
        class JobSearchRequest(BaseModel):
            keyword: Optional[str] = None
            location: Optional[str] = None
            page: int = Field(default=1, ge=1)
            limit: int = Field(default=10, ge=1, le=50)
        
        class JobSearchResult(BaseModel):
            id: UUID
            title: str
            company_name: str  # From recruiter's email for MVP
            location_type: str
            posted_date: str  # Relative format
            description_snippet: str
        
        class JobSearchResponse(BaseModel):
            results: List[JobSearchResult]
            total_count: int
            page: int
            total_pages: int
        ```

- [ ] **Task 3: Search Service Layer (AC: 2-6)**
    - [ ] In `backend/app/modules/jobs/service.py`, implement:
        ```python
        async def search_jobs(
            db: AsyncSession,
            keyword: Optional[str],
            location: Optional[str],
            page: int = 1,
            limit: int = 10
        ) -> Tuple[List[JobDescription], int]:
            # Build dynamic query with filters
            query = select(JobDescription).where(JobDescription.is_active == True)
            
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.where(
                    or_(
                        JobDescription.title.ilike(search_pattern),
                        JobDescription.description.ilike(search_pattern)
                    )
                )
            
            if location:
                location_normalized = location.lower().strip()
                if location_normalized in ['remote', 'hybrid', 'on-site']:
                    query = query.where(JobDescription.location_type == location_normalized)
            
            # Count total before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await db.scalar(count_query)
            
            # Apply pagination and sorting
            query = query.order_by(JobDescription.uploaded_at.desc())
            query = query.offset((page - 1) * limit).limit(limit)
            
            result = await db.execute(query)
            jobs = result.scalars().all()
            
            return jobs, total_count
        ```

- [ ] **Task 4: API Endpoint (AC: All)**
    - [ ] In `backend/app/modules/jobs/router.py`, create:
        ```python
        @router.get("/search/basic", response_model=schemas.JobSearchResponse)
        async def search_jobs_basic(
            keyword: Optional[str] = Query(None, max_length=200),
            location: Optional[str] = Query(None, max_length=50),
            page: int = Query(1, ge=1),
            limit: int = Query(10, ge=1, le=50),
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(require_job_seeker)  # Only job_seeker and admin
        ):
            """
            Search for job descriptions by keyword and/or location.
            Returns paginated results sorted by newest first.
            """
            jobs, total_count = await service.search_jobs(
                db=db,
                keyword=keyword,
                location=location,
                page=page,
                limit=limit
            )
            
            # Transform to response format
            results = [
                schemas.JobSearchResult(
                    id=job.id,
                    title=job.title,
                    company_name=job.recruiter.email,  # MVP: use email
                    location_type=job.location_type,
                    posted_date=format_relative_time(job.uploaded_at),
                    description_snippet=job.description[:150] + "..." if len(job.description) > 150 else job.description
                )
                for job in jobs
            ]
            
            total_pages = (total_count + limit - 1) // limit
            
            return schemas.JobSearchResponse(
                results=results,
                total_count=total_count,
                page=page,
                total_pages=total_pages
            )
        ```

- [ ] **Task 5: Testing (AC: All)**
    - [ ] In `backend/tests/modules/jobs/test_search_service.py`:
        - [ ] `test_search_by_keyword_only` - Verify keyword search works
        - [ ] `test_search_by_location_only` - Verify location filter works
        - [ ] `test_search_combined` - Verify AND condition works
        - [ ] `test_search_no_results` - Verify empty results handling
        - [ ] `test_search_pagination` - Verify pagination logic
        - [ ] `test_search_case_insensitive` - Verify ILIKE works
    - [ ] In `backend/tests/modules/jobs/test_job_router.py`:
        - [ ] `test_search_endpoint_unauthorized` - Verify auth required
        - [ ] `test_search_endpoint_job_seeker` - Verify job_seeker can search
        - [ ] `test_search_endpoint_recruiter_forbidden` - Verify recruiter cannot search (only upload JDs)
        - [ ] `test_search_endpoint_validation` - Verify query param validation

### Frontend Implementation

- [ ] **Task 6: Server Actions for Search (AC: All)**
    - [ ] Create `frontend/features/jobs/actions.ts`:
        ```typescript
        'use server';
        
        import { cookies } from 'next/headers';
        import apiClient from '@/services/api-client';
        
        export async function searchJobsAction(
          keyword?: string,
          location?: string,
          page: number = 1
        ) {
          try {
            const cookieStore = await cookies();
            const token = cookieStore.get('access_token')?.value;
            
            if (!token) {
              return { error: 'Unauthorized' };
            }
            
            const response = await apiClient.get('/jobs/search/basic', {
              params: { keyword, location, page, limit: 10 },
              headers: { Authorization: `Bearer ${token}` }
            });
            
            return { data: response.data };
          } catch (error) {
            console.error('Search jobs error:', error);
            return { error: 'Failed to search jobs' };
          }
        }
        ```

- [ ] **Task 7: Search Page UI (AC: 1, 5, 7, 8)**
    - [ ] Create `frontend/app/jobs/search/page.tsx`:
        ```typescript
        'use client';
        
        import { useState } from 'react';
        import { Input } from '@/components/ui/input';
        import { Button } from '@/components/ui/button';
        import { JobCard } from '@/features/jobs/components/JobCard';
        import { Pagination } from '@/components/common/Pagination';
        import { searchJobsAction } from '@/features/jobs/actions';
        import { useToast } from '@/hooks/use-toast';
        
        export default function JobSearchPage() {
          const [keyword, setKeyword] = useState('');
          const [location, setLocation] = useState('');
          const [results, setResults] = useState(null);
          const [loading, setLoading] = useState(false);
          const [page, setPage] = useState(1);
          const { toast } = useToast();
          
          const handleSearch = async (newPage = 1) => {
            setLoading(true);
            const { data, error } = await searchJobsAction(keyword, location, newPage);
            setLoading(false);
            
            if (error) {
              toast({
                title: "Lỗi tìm kiếm",
                description: "Đã xảy ra lỗi khi tìm kiếm. Vui lòng thử lại sau.",
                variant: "destructive"
              });
              return;
            }
            
            setResults(data);
            setPage(newPage);
          };
          
          return (
            <div className="container mx-auto py-8">
              <h1 className="text-3xl font-bold mb-6">Tìm kiếm việc làm</h1>
              
              {/* Search Form */}
              <div className="bg-white p-6 rounded-lg shadow mb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Từ khóa</label>
                    <Input
                      placeholder="e.g., Python Developer, Data Scientist"
                      value={keyword}
                      onChange={(e) => setKeyword(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Địa điểm</label>
                    <Input
                      placeholder="e.g., Hà Nội, Hồ Chí Minh, Remote"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                    />
                  </div>
                </div>
                <Button
                  onClick={() => handleSearch(1)}
                  disabled={loading}
                  className="w-full md:w-auto"
                >
                  {loading ? 'Đang tìm kiếm...' : 'Tìm kiếm'}
                </Button>
              </div>
              
              {/* Results */}
              {loading && <div>Loading skeleton cards...</div>}
              
              {!loading && results && results.total_count === 0 && (
                <div className="text-center py-12">
                  <p className="text-lg text-gray-600 mb-2">
                    Không tìm thấy tin tuyển dụng nào phù hợp với tiêu chí của bạn.
                  </p>
                  <p className="text-sm text-gray-500">
                    Thử điều chỉnh từ khóa hoặc mở rộng phạm vi địa điểm.
                  </p>
                </div>
              )}
              
              {!loading && results && results.total_count > 0 && (
                <>
                  <div className="mb-4 text-sm text-gray-600">
                    Showing {(page - 1) * 10 + 1}-{Math.min(page * 10, results.total_count)} of {results.total_count} results
                  </div>
                  <div className="grid gap-4 mb-8">
                    {results.results.map((job) => (
                      <JobCard key={job.id} job={job} />
                    ))}
                  </div>
                  <Pagination
                    currentPage={page}
                    totalPages={results.total_pages}
                    onPageChange={(newPage) => handleSearch(newPage)}
                  />
                </>
              )}
            </div>
          );
        }
        ```

- [ ] **Task 8: Job Card Component (AC: 2)**
    - [ ] Create `frontend/features/jobs/components/JobCard.tsx`:
        ```typescript
        interface JobCardProps {
          job: {
            id: string;
            title: string;
            company_name: string;
            location_type: string;
            posted_date: string;
            description_snippet: string;
          };
        }
        
        export function JobCard({ job }: JobCardProps) {
          return (
            <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
              <h3 className="text-xl font-semibold mb-2">{job.title}</h3>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <span>📧 {job.company_name}</span>
                <span>📍 {job.location_type}</span>
                <span>🕒 {job.posted_date}</span>
              </div>
              <p className="text-gray-700 mb-4">{job.description_snippet}</p>
              <Button variant="outline" size="sm">
                Xem chi tiết
              </Button>
            </div>
          );
        }
        ```

- [ ] **Task 9: Pagination Component (AC: 6)**
    - [ ] Create or reuse `frontend/components/common/Pagination.tsx`:
        ```typescript
        interface PaginationProps {
          currentPage: number;
          totalPages: number;
          onPageChange: (page: number) => void;
        }
        
        export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
          return (
            <div className="flex justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === 1}
                onClick={() => onPageChange(currentPage - 1)}
              >
                Previous
              </Button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={page === currentPage ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onPageChange(page)}
                >
                  {page}
                </Button>
              ))}
              
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => onPageChange(currentPage + 1)}
              >
                Next
              </Button>
            </div>
          );
        }
        ```

- [ ] **Task 10: Navigation Integration (AC: 1)**
    - [ ] Add "Tìm kiếm việc làm" link to job_seeker navigation in `frontend/components/common/Navigation.tsx`:
        ```typescript
        {user.role === 'job_seeker' && (
          <>
            <Link href="/cvs">My CVs</Link>
            <Link href="/jobs/search">🔍 Tìm việc làm</Link>  {/* NEW */}
          </>
        )}
        ```

## Dev Notes

### Architecture Context

**Critical Coding Standards:**
- ✅ **Authentication**: Use HttpOnly cookies - NEVER access `document.cookie` in client components
- ✅ **Server Actions**: All API calls from client components MUST use Server Actions (`'use server'`)
- ✅ **Role-Based Access**: Search endpoint is protected for `job_seeker` only (admin also has access)
- ✅ **API Service Layer**: Centralize API interactions in `/services/api-client.ts`
- ✅ **DRY Principle**: Reuse existing `Pagination`, `Button`, `Input` components from shadcn/ui

### Database Schema

**Table: `job_descriptions`**
- Located: `backend/app/modules/jobs/models.py`
- Key columns for this story:
  - `title` VARCHAR(255) - Job title for keyword search
  - `description` TEXT - Full job description for keyword search
  - `location_type` VARCHAR(50) - Filter: 'remote', 'hybrid', 'on-site'
  - `uploaded_at` TIMESTAMP - Sorting: newest first
  - `is_active` BOOLEAN - Filter only active jobs
  - `user_id` UUID - FK to recruiter who posted

**Indexes Needed:**
```sql
-- GIN index for full-text search on title + description
CREATE INDEX idx_job_descriptions_search 
ON job_descriptions USING gin(to_tsvector('english', title || ' ' || description));

-- B-tree index for location filtering
CREATE INDEX idx_job_descriptions_location ON job_descriptions(location_type);

-- B-tree index for sorting by newest first
CREATE INDEX idx_job_descriptions_uploaded_at ON job_descriptions(uploaded_at DESC);
```

### API Specification

**Endpoint:** `GET /api/v1/jobs/search/basic`

**Query Parameters:**
- `keyword` (optional): string, max 200 chars - Keyword to search in title/description
- `location` (optional): string, max 50 chars - Location type filter
- `page` (optional): int, default 1, min 1 - Current page number
- `limit` (optional): int, default 10, min 1, max 50 - Results per page

**Request Example:**
```http
GET /api/v1/jobs/search/basic?keyword=Python%20Developer&location=remote&page=1&limit=10
Cookie: access_token=<HttpOnly JWT>
```

**Response Schema:**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Senior Python Developer",
      "company_name": "recruiter@example.com",
      "location_type": "remote",
      "posted_date": "2 days ago",
      "description_snippet": "We are looking for an experienced Python developer..."
    }
  ],
  "total_count": 47,
  "page": 1,
  "total_pages": 5
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication cookie
- `403 Forbidden`: User role is not `job_seeker` or `admin`
- `422 Validation Error`: Invalid query parameters
- `500 Internal Server Error`: Database or server error

### Technical Decisions

**1. Search Implementation: ILIKE vs Full-Text Search**

For MVP (Story 9.1), we're using **PostgreSQL ILIKE** for simplicity:
```python
JobDescription.title.ilike(f"%{keyword}%")
```

**Pros:**
- Simple to implement
- Works for basic keyword matching
- No additional setup required

**Future Enhancement (Story 9.2):**
- Upgrade to PostgreSQL Full-Text Search (FTS) with `to_tsvector` and `to_tsquery`
- Better Vietnamese language support
- Ranking by relevance score (`ts_rank`)

**2. Location Filter: Exact Match**

For MVP, location filter uses **exact match** on `location_type` enum:
- User enters: "remote" → Matches jobs with `location_type = 'remote'`
- User enters: "Hà Nội" → No match (we don't have city-level location yet)

**Future Enhancement (Story 9.3):**
- Add `city` column to `job_descriptions` table
- Support semantic location search (e.g., "Hà Nội" matches "Hanoi", "Ha Noi")

**3. Pagination: Offset-Based**

Using simple **offset-based pagination**:
```python
query.offset((page - 1) * limit).limit(limit)
```

**Trade-offs:**
- ✅ Easy to implement
- ✅ Works well for < 10,000 results
- ⚠️ Performance degrades with deep pagination (page 100+)

**Future Optimization:**
- Consider cursor-based pagination if job count grows significantly

### Component Hierarchy

```
app/jobs/search/page.tsx (Client Component)
├── SearchForm
│   ├── Input (shadcn/ui) - Keyword
│   ├── Input (shadcn/ui) - Location
│   └── Button (shadcn/ui) - Search
├── JobCard (feature-specific)
│   ├── Job title, company, location, date
│   ├── Description snippet
│   └── Button (shadcn/ui) - View details
└── Pagination (common component)
    ├── Button - Previous
    ├── Button[] - Page numbers
    └── Button - Next
```

### Error Handling Strategy

**Backend:**
1. **Validation errors** (422): Caught by Pydantic schema validation
2. **Database errors**: Log error, return 500 with generic message
3. **Empty results**: Return 200 with `total_count: 0` (not an error)

**Frontend:**
1. **API errors**: Show toast notification with user-friendly message
2. **Network timeout**: Retry button in error state
3. **Empty results**: Show helpful message with suggestions

### Testing Strategy

**Backend Tests:**
- **Unit tests** (`test_search_service.py`):
  - Test search logic with various combinations
  - Test pagination calculations
  - Test edge cases (empty keyword, invalid location)
- **Integration tests** (`test_job_router.py`):
  - Test API endpoint with real database
  - Test authentication and authorization
  - Test query parameter validation

**Frontend Tests:**
- **Component tests**:
  - Test JobCard renders correctly
  - Test Pagination button states
  - Test SearchForm submission
- **Integration tests**:
  - Test search flow end-to-end
  - Test loading states
  - Test error handling

### Performance Considerations

**Expected Load:**
- MVP: < 1,000 job descriptions
- Concurrent searches: < 50 per minute
- Search response time target: < 500ms

**Optimizations:**
1. **Database indexes** on search columns (see Database Schema section)
2. **Eager loading** of recruiter relationship to avoid N+1 queries:
   ```python
   query = query.options(selectinload(JobDescription.recruiter))
   ```
3. **Limit result set** to max 50 items per page to prevent large payloads

### Future Enhancements (Out of Scope for 9.1)

Story 9.2 will add:
- Advanced filters (salary range, experience level, skills)
- Full-text search with relevance ranking
- Sort options (date, salary, relevance)

Story 9.3 will add:
- Semantic search using vector embeddings (pgvector)
- Personalized job recommendations based on CV

Story 9.4 will add:
- Save search queries
- Job alerts via email
- Apply to jobs directly from search results

### Dependencies

**Backend:**
- `sqlalchemy[asyncio]` - Already installed
- `asyncpg` - Already installed (PostgreSQL async driver)
- No new dependencies required

**Frontend:**
- `@/components/ui` - Already available (shadcn/ui)
- `next/navigation` - Already available (Next.js)
- No new dependencies required

### Checklist Before Dev Starts

- [ ] Verify `job_descriptions` table exists and has required columns
- [ ] Verify `require_job_seeker` guard exists in `backend/app/modules/auth/dependencies.py`
- [ ] Verify Next.js Server Actions are configured (React 19+)
- [ ] Verify shadcn/ui components (`Input`, `Button`) are installed
- [ ] Read coding-standards.md for HttpOnly cookie handling rules
- [ ] Read backend-architecture.md for service layer patterns
- [ ] Read frontend-architecture.md for Server Actions patterns

### Reference Files

**Backend:**
- `backend/app/modules/jobs/models.py` - JobDescription model
- `backend/app/modules/jobs/schemas.py` - API schemas
- `backend/app/modules/jobs/service.py` - Business logic
- `backend/app/modules/jobs/router.py` - API endpoints
- `backend/app/modules/auth/dependencies.py` - Auth guards

**Frontend:**
- `frontend/app/jobs/search/page.tsx` - Search page (NEW)
- `frontend/features/jobs/actions.ts` - Server Actions (NEW)
- `frontend/features/jobs/components/JobCard.tsx` - Job card component (NEW)
- `frontend/components/common/Pagination.tsx` - Pagination component (may exist or NEW)
- `frontend/lib/auth.ts` - Auth utilities

**Architecture:**
- `_bmad-output/planning-artifacts/architecture/coding-standards.md`
- `_bmad-output/planning-artifacts/architecture/backend-architecture.md`
- `_bmad-output/planning-artifacts/architecture/frontend-architecture.md`
- `_bmad-output/planning-artifacts/architecture/data-models-and-apis.md`

### Git Commit Pattern Reference

Based on recent commits:
```
feat(jobs): Implement basic job search with keyword and location filters

- Add search endpoint GET /api/v1/jobs/search/basic
- Implement service layer search logic with ILIKE and pagination
- Create job search page at /jobs/search with search form
- Add JobCard component for displaying search results
- Add pagination component for result navigation
- Add database indexes for search performance
- Add unit and integration tests for search functionality

Closes #9.1
```

## Definition of Done

- [ ] All acceptance criteria (AC1-AC8) are met and verified
- [ ] All backend tasks (1-5) are completed with passing tests
- [ ] All frontend tasks (6-10) are completed and render correctly
- [ ] Code follows project coding standards (HttpOnly cookies, Server Actions, DRY)
- [ ] Unit tests written and passing (> 80% coverage for new code)
- [ ] Integration tests written and passing
- [ ] No regressions in existing functionality
- [ ] API endpoint documented in `data-models-and-apis.md`
- [ ] Database migrations applied (if schema changes required)
- [ ] Peer code review completed
- [ ] Manual testing completed on dev environment
- [ ] Search performance verified (< 500ms response time)
- [ ] Loading and error states tested manually

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Debug Log References
_To be filled by dev agent_

### Completion Notes List
_To be filled by dev agent_

### File List
_To be filled by dev agent_
