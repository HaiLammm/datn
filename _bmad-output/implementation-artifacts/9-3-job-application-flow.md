# Story 9.3: Job Application Flow

Status: ready-for-dev

## Story

As a Job Seeker,
I want to view job details and submit an application with my CV and cover letter,
So that I can apply for jobs that match my skills and interests.

## Acceptance Criteria

### Backend Requirements

1. **Application Model** (✅ COMPLETED)
   - **Given** the system needs to track applications, **When** a Job Seeker applies for a job, **Then** the application data is stored with `job_id`, `user_id`, `cv_id`, `cover_letter`, `status`, and timestamps
   - **Given** a user tries to apply for the same job twice, **When** they submit, **Then** system returns error due to unique constraint on (`user_id`, `job_id`)
   - **Status values:** `pending`, `reviewed`, `shortlisted`, `rejected`, `accepted`, `hired`

2. **Job Detail Endpoint** (✅ COMPLETED)
   - **Given** a Job Seeker or anonymous user wants to view job details, **When** they request `GET /api/v1/jobs/{id}`, **Then** system returns complete job info including title, description, benefits, salary, location, job_type
   - **Public access:** No authentication required

3. **Apply Endpoint** (✅ COMPLETED)
   - **Given** an authenticated Job Seeker, **When** they `POST /api/v1/jobs/{id}/apply` with `cv_id` and optional `cover_letter`, **Then** application is created
   - **Validations:**
     - CV belongs to the authenticated user
     - Job exists and is active
     - User hasn't already applied to this job
   - **Error cases:**
     - 401 if not authenticated
     - 403 if CV doesn't belong to user
     - 404 if job not found
     - 409 if duplicate application

### Frontend Requirements

4. **Job Service & Types** (✅ COMPLETED)
   - **Given** frontend needs to interact with job API, **When** making requests, **Then** use centralized service layer
   - Methods: `getJobDetail(id)`, `applyJob(jobId, cvId, coverLetter)`
   - Types defined in `@datn/shared-types`

5. **Job Detail Page** (✅ COMPLETED)
   - **Given** a user navigates to `/jobs/[id]`, **When** page loads, **Then** display:
     - Job title, company info (if available)
     - Salary range (if provided)
     - Location and job type
     - Full description
     - Required skills
     - Benefits list
     - "Apply Now" button (sticky on mobile, sidebar on desktop)
   - **SEO:** Generate metadata with job title and description

6. **Application Modal/Dialog** (✅ COMPLETED)
   - **Given** a Job Seeker clicks "Apply Now", **When** modal opens, **Then** display:
     - List of user's active CVs (radio selection)
     - Textarea for optional cover letter
     - Submit button with loading state
   - **Given** user has no CVs, **When** modal opens, **Then** show message with link to upload CV
   - **Given** user submits successfully, **When** application is created, **Then** show success toast and close modal

## Dev Notes

### 🎯 Implementation Summary

**Status:** Story 9.3 has been fully implemented in commit `a321289`. All backend and frontend components are complete and functional.

**Commit:** `a321289 - feat(jobs): implement job application flow and active filters (Store 9.2, 9.3)`

### 📂 Files Modified/Created

#### Backend Files
- ✅ `backend/app/modules/jobs/models.py` - Added `Application` model with unique constraint
- ✅ `backend/app/modules/jobs/schemas.py` - Added `ApplicationCreate`, `ApplicationResponse` schemas
- ✅ `backend/app/modules/jobs/services.py` - Added `apply_to_job()`, `get_job_detail()` methods
- ✅ `backend/app/modules/jobs/router.py` - Added `POST /jobs/{id}/apply`, `GET /jobs/{id}` endpoints
- ✅ `backend/alembic/versions/c2b9997dde66_create_applications_table.py` - Migration for applications table

#### Frontend Files
- ✅ `frontend/app/jobs/[id]/page.tsx` - Job detail page (SSR with metadata)
- ✅ `frontend/features/jobs/components/JobDetailClient.tsx` - Client component for job detail
- ✅ `frontend/features/jobs/components/ApplyJobDialog.tsx` - Application modal component
- ✅ `frontend/services/job.service.ts` - Added `getJobDetail()`, `applyJob()` methods
- ✅ `frontend/features/jobs/actions.ts` - Server actions for job operations
- ✅ `packages/shared-types/src/job.ts` - Added `ApplicationCreate`, `ApplicationResponse` types

### 🏗️ Architecture Compliance

#### Critical Fullstack Rules (Coding Standards)
✅ **HttpOnly Cookies:** All authenticated requests use Server Actions - no `document.cookie` access  
✅ **API Service Layer:** `job.service.ts` centralizes all API calls - no direct fetch in components  
✅ **Type Sharing:** All types defined in `@datn/shared-types` and imported  
✅ **Backend Modularity:** Logic in `modules/jobs/` following `router.py`, `service.py`, `schemas.py`, `models.py` pattern  
✅ **Protected Routes:** Application submission uses Server Actions with cookie-based auth  

#### SQLAlchemy Async Rules
✅ **Unique Constraint:** `UniqueConstraint('user_id', 'job_id')` prevents duplicate applications  
✅ **Eager Loading:** When fetching applications with relations, use `selectinload()` (future enhancement)  
✅ **Relationship Handling:** Proper FK setup with `ondelete="CASCADE"` and `ondelete="SET NULL"` for cv_id  

#### Component Hierarchy
```
lib/hooks/                              [Not needed for this story]
components/common/                      [Reused: Dialog, Button, RadioGroup, Textarea]
features/jobs/components/               [NEW: ApplyJobDialog, JobDetailClient]
app/jobs/[id]/                          [NEW: Job detail page]
```

### 🗄️ Database Schema (Applications Table)

```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES cvs(id) ON DELETE SET NULL,  -- Allow NULL if CV deleted
    cover_letter TEXT,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT uq_user_job_application UNIQUE (user_id, job_id),
    CONSTRAINT check_application_status CHECK (
        status IN ('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted', 'hired')
    )
);

CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
```

### 🔌 API Endpoints

#### GET /api/v1/jobs/{id}
**Purpose:** Fetch detailed job information  
**Auth:** Public (no authentication required)  
**Response:**
```typescript
{
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
}
```

#### POST /api/v1/jobs/{id}/apply
**Purpose:** Submit job application  
**Auth:** Required (Job Seeker role)  
**Request Body:**
```typescript
{
  cv_id: string;        // UUID of CV belonging to user
  cover_letter?: string; // Optional cover letter
}
```
**Response:**
```typescript
{
  id: string;
  job_id: string;
  user_id: number;
  cv_id: string;
  cover_letter: string | null;
  status: "pending";
  created_at: string;
  updated_at: string;
}
```

**Error Responses:**
- `401 Unauthorized` - User not authenticated
- `403 Forbidden` - CV doesn't belong to user
- `404 Not Found` - Job or CV not found
- `409 Conflict` - User already applied to this job

### 🎨 Frontend Components

#### ApplyJobDialog Component
**Location:** `frontend/features/jobs/components/ApplyJobDialog.tsx`

**Props:**
```typescript
interface ApplyJobDialogProps {
  job: JobDescriptionResponse;  // Job data to display in modal
  trigger?: React.ReactNode;    // Custom trigger button (optional)
}
```

**Features:**
- Fetches user's CV list when modal opens
- Radio selection for CV (defaults to first CV)
- Optional cover letter textarea
- Validation: Requires at least one CV
- Loading states for CV fetch and application submission
- Success/error toast notifications
- Link to CV upload if no CVs exist

**State Management:**
- `open` - Modal visibility
- `cvs` - List of user CVs
- `loadingCVs` - CV fetch loading state
- `selectedCV` - Selected CV ID
- `coverLetter` - Cover letter text
- `applying` - Application submission loading state

#### JobDetailClient Component
**Location:** `frontend/features/jobs/components/JobDetailClient.tsx`

**Features:**
- Responsive layout (sidebar on desktop, sticky button on mobile)
- Job information display sections:
  - Title and metadata (location, job type, posted date)
  - Salary range (if available)
  - Description (formatted)
  - Required skills (badge list)
  - Benefits (bullet list)
- Apply button integration with `ApplyJobDialog`
- Skeleton loading states (if needed for client-side refetch)

### 🧪 Testing Considerations

**Manual Testing Checklist:**
- [ ] Public access: Anonymous user can view job details
- [ ] Authenticated Job Seeker can open apply modal
- [ ] Modal shows list of user's CVs
- [ ] Modal shows "no CVs" message with upload link if user has 0 CVs
- [ ] Cannot submit without selecting a CV
- [ ] Cover letter is optional
- [ ] Success toast after successful application
- [ ] Error toast if duplicate application (409 Conflict)
- [ ] Error toast if CV doesn't belong to user (403 Forbidden)
- [ ] Modal closes after successful submission

**Database Testing:**
- [ ] Unique constraint prevents duplicate applications
- [ ] Application status defaults to "pending"
- [ ] Timestamps (created_at, updated_at) are set correctly
- [ ] Foreign key constraints work (CASCADE for job/user, SET NULL for cv)

### 📝 Code Patterns Established

#### Server-Side Job Data Fetching (SSR)
```typescript
// frontend/app/jobs/[id]/page.tsx
export default async function JobDetailPage(props: PageProps) {
  const params = await props.params;
  const job = await jobService.getJobDetail(params.id); // SSR fetch
  return <JobDetailClient job={job} />;
}
```

#### Service Layer Pattern
```typescript
// frontend/services/job.service.ts
async applyJob(jobId: string, cvId: string, coverLetter?: string) {
  const response = await apiClient.post(`/jobs/${jobId}/apply`, {
    cv_id: cvId,
    cover_letter: coverLetter || null,
  });
  return response.data;
}
```

#### Backend Service Pattern
```python
# backend/app/modules/jobs/services.py
async def apply_to_job(
    db: AsyncSession,
    job_id: uuid.UUID,
    cv_id: uuid.UUID,
    user_id: int,
    cover_letter: Optional[str] = None
) -> Application:
    # 1. Validate job exists and is active
    # 2. Validate CV belongs to user
    # 3. Check for duplicate application
    # 4. Create application record
    # 5. Commit and return
```

### 🔗 Related Stories & Dependencies

**Dependencies (Completed):**
- ✅ Story 1.1-1.3: User authentication and profile (Epic 1)
- ✅ Story 2.1: CV upload functionality (Epic 2)
- ✅ Story 9.1: Basic job search (Epic 9)

**Future Enhancements:**
- Story 9.4: Job recommendations (ML-based suggestions)
- Epic 7: Real-time messaging (Recruiter can contact applicants)
- Future: Application tracking for Job Seekers (view status, withdraw)
- Future: Recruiter dashboard to review applications

### ⚠️ Known Issues & Technical Debt

**Current Limitations:**
1. **No Application Tracking for Job Seekers:** Users can apply but cannot view their application status or history
2. **No Withdraw Functionality:** Users cannot cancel/withdraw applications
3. **No Recruiter View:** Recruiters cannot yet see applicants for their jobs (planned for separate story)
4. **No Email Notifications:** No email sent to recruiter when new application received
5. **No Application Analytics:** No tracking of application metrics (conversion rate, time to apply, etc.)

**Performance Considerations:**
- CV list fetch on modal open: Consider caching CV list in context/state if user applies to multiple jobs in same session
- Job detail page: Consider caching job data if implementing client-side navigation

### 🚀 Future Stories (Recommendations)

1. **Story 9.3.1: Application Tracking Dashboard** (Job Seeker)
   - View all applications with status
   - Filter by status (pending, reviewed, etc.)
   - Withdraw application functionality
   - Application timeline/history

2. **Story 9.3.2: Recruiter Application Management**
   - View applicants for each job posting
   - Filter/sort applicants
   - Update application status
   - View applicant CV and cover letter
   - Initiate chat with applicant (links to Epic 7)

3. **Story 9.3.3: Application Notifications**
   - Email to recruiter on new application
   - Email to job seeker on status change
   - In-app notifications for both roles

### 📚 References

- [Source: _bmad-output/planning-artifacts/architecture/coding-standards.md#Critical Fullstack Rules]
- [Source: _bmad-output/planning-artifacts/architecture/coding-standards.md#SQLAlchemy Async Rules]
- [Source: _bmad-output/planning-artifacts/architecture/database-schema.md#Applications Table]
- [Source: _bmad-output/planning-artifacts/architecture/api-specification.md#Job Endpoints]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 9: Advanced Job Search Application]

---

## Dev Agent Record

### Agent Model Used
(To be filled by Dev agent when working on this story)

### Completion Notes List
- ✅ 2026-01-06: All backend and frontend functionality implemented in commit a321289
- ✅ Applications table created with proper constraints and indexes
- ✅ Job detail page with SSR and SEO metadata
- ✅ Apply dialog with CV selection and cover letter
- ✅ Full validation and error handling

### File List
**Backend:**
- `backend/app/modules/jobs/models.py` - Application model
- `backend/app/modules/jobs/schemas.py` - Application schemas
- `backend/app/modules/jobs/services.py` - Business logic
- `backend/app/modules/jobs/router.py` - API endpoints
- `backend/alembic/versions/c2b9997dde66_create_applications_table.py` - Migration

**Frontend:**
- `frontend/app/jobs/[id]/page.tsx` - Job detail page
- `frontend/features/jobs/components/JobDetailClient.tsx` - Client component
- `frontend/features/jobs/components/ApplyJobDialog.tsx` - Apply modal
- `frontend/services/job.service.ts` - API service methods
- `frontend/features/jobs/actions.ts` - Server actions

**Shared:**
- `packages/shared-types/src/job.ts` - TypeScript types
