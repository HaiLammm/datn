# Epic 6: Job Seeker UX Enhancements

## 6.1. Goals and Background Context

### 6.1.1. Goals

- Hoan thien trai nghiem nguoi dung cho Job Seekers
- Trien khai CV history management (xem, xoa CVs da upload)
- Cung cap tinh nang user profile management
- Cai thien feedback loop va UX cho CV analysis flow
- Dam bao data privacy voi CV deletion feature

### 6.1.2. Background Context

He thong hien tai da co:
- CV upload va analysis (Epic 2 - da hoan thanh)
- Hybrid Skill Scoring voi detailed breakdown (Epic 5 - da hoan thanh)

Can bo sung de hoan thien Job Seeker experience:
- CV history list va management
- Delete CV va associated data
- User profile page
- Better loading states va feedback

**PRD Requirements Addressed:**
| Requirement | Description |
|-------------|-------------|
| **FR14** | Allow job seekers to delete CVs and associated data |
| **FR15** | Display history list of uploaded CVs and analysis results |
| **FR12** | Integrate CV analysis features with consistent UI |

**From Project Brief:**
- CV version history and improvement tracking
- Privacy & Data Control (user-controlled data deletion)
- Transparent data usage policies

### 6.1.3. Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-17 | 0.1.0 | Initial PRD draft for Job Seeker UX | John (PM) |

---

## 6.2. Requirements

### 6.2.1. Functional Requirements

| ID | Requirement |
|----|-------------|
| **FR-UX1** | He thong phai hien thi danh sach tat ca CVs user da upload |
| **FR-UX2** | CV list phai hien thi: filename, upload date, quality score, status |
| **FR-UX3** | User phai co the xem chi tiet analysis cua bat ky CV nao trong history |
| **FR-UX4** | User phai co the xoa CV va tat ca associated data |
| **FR-UX5** | Deletion phai co confirmation dialog voi clear warning |
| **FR-UX6** | User phai co the xem va edit profile information |
| **FR-UX7** | Profile page hien thi account info, stats, settings |
| **FR-UX8** | He thong phai co proper loading states cho async operations |
| **FR-UX9** | He thong phai hien thi meaningful error messages |
| **FR-UX10** | User phai co the compare CVs (optional - nice to have) |

### 6.2.2. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| **NFR-UX1** | CV list phai load efficiently voi pagination |
| **NFR-UX2** | Deletion phai cascade tat ca related data |
| **NFR-UX3** | UI phai consistent voi existing design |
| **NFR-UX4** | All user actions phai co clear feedback |

### 6.2.3. Compatibility Requirements

| ID | Requirement |
|----|-------------|
| **CR-UX1** | CV history phai work voi existing CV module |
| **CR-UX2** | Profile phai integrate voi existing auth |
| **CR-UX3** | Responsive design cho all screens |

---

## 6.3. User Interface Enhancement Goals

### 6.3.1. Screen Updates

| Screen | Description |
|--------|-------------|
| **Dashboard** | Enhanced voi CV history preview |
| **CV History Page** | Full list voi filters va sorting |
| **CV Detail Page** | Enhanced voi delete option |
| **Profile Page** | User account information |
| **Settings Page** | Account settings, preferences |

### 6.3.2. UI Mockup

```
+-------------------------------------------------------------+
|                    Job Seeker Dashboard                      |
+-------------------------------------------------------------+
|  Welcome back, Hai Lam!                      [Profile v]    |
|                                                             |
|  +-------------------------------------------------------------+
|  |                    Quick Actions                        |
|  |  [+ Upload New CV]         [View CV History]            |
|  +-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  |  Your CVs (3 total)                       [View All ->]  |
|  |  +-----------------------------------------------------+|
|  |  | my_cv_v3.pdf          Score: 78   12/15/2025    ||
|  |  | resume_updated.docx   Score: 65   12/10/2025    ||
|  |  | first_cv.pdf          Score: 52   12/01/2025    ||
|  |  +-----------------------------------------------------+|
|  +-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  |  Skill Progress                                         |
|  |  Total unique skills: 15                                |
|  |  Your top skills: Python, React, FastAPI                |
|  |  Recommended to learn: Kubernetes, Docker               |
|  +-------------------------------------------------------------+
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                      CV History                              |
+-------------------------------------------------------------+
|  Search: [____________]  Sort by: [Date v]  Filter: [All v]|
|                                                             |
|  +-------------------------------------------------------------+
|  | my_cv_v3.pdf                                        |
|  |    Uploaded: Dec 15, 2025 at 10:30 AM                  |
|  |    Score: 78/100  ========..                           |
|  |    Skills: Python, React, FastAPI (+12 more)           |
|  |                                                         |
|  |    [View Analysis]  [Download]  [Delete]            |
|  +-------------------------------------------------------------+
|  +-------------------------------------------------------------+
|  | resume_updated.docx                                 |
|  |    Uploaded: Dec 10, 2025 at 2:15 PM                   |
|  |    Score: 65/100  ======....                           |
|  |    Skills: JavaScript, Node.js (+8 more)               |
|  |                                                         |
|  |    [View Analysis]  [Download]  [Delete]            |
|  +-------------------------------------------------------------+
|                                                             |
|  Showing 1-10 of 3 CVs                                      |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                    Delete Confirmation                       |
+-------------------------------------------------------------+
|                                                             |
|  !  Are you sure you want to delete this CV?              |
|                                                             |
|  my_cv_v3.pdf                                           |
|                                                             |
|  This action will permanently delete:                       |
|  - The uploaded CV file                                     |
|  - All analysis results                                     |
|  - Extracted skills data                                    |
|                                                             |
|  This action cannot be undone.                              |
|                                                             |
|              [Cancel]    [Delete Permanently]               |
|                                                             |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                      My Profile                              |
+-------------------------------------------------------------+
|                                                             |
|  +---------+  Hai Lam                                      |
|  | Avatar  |  hailam@example.com                           |
|  |         |  Member since: Dec 1, 2025                    |
|  +---------+                                               |
|                                                             |
|  +-------------------------------------------------------------+
|  |  Account Statistics                                     |
|  |                                                         |
|  |  CVs Uploaded:     3                                 |
|  |  Average Score:    65                                |
|  |  Best Score:       78                                |
|  |  Skills Tracked:   15                                |
|  +-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  |  Account Actions                                        |
|  |                                                         |
|  |  [Change Password]                                      |
|  |  [Delete Account]   ! This will delete all your data  |
|  +-------------------------------------------------------------+
|                                                             |
+-------------------------------------------------------------+
```

---

## 6.4. Technical Assumptions

### 6.4.1. API Endpoints

```yaml
# CV History endpoints
GET    /api/v1/cvs                    # List user's CVs (already exists, enhance)
DELETE /api/v1/cvs/{cv_id}            # Delete CV (already exists, verify cascade)
GET    /api/v1/cvs/{cv_id}/download   # Download original CV file

# Profile endpoints
GET    /api/v1/users/me               # Get current user (already exists)
PATCH  /api/v1/users/me               # Update user profile
GET    /api/v1/users/me/stats         # Get user statistics
DELETE /api/v1/users/me               # Delete account (with all data)
```

### 6.4.2. Data Cascade on Delete

```python
# When deleting CV, cascade delete:
# - cv_analyses records (FK with CASCADE)
# - cv file from storage
# - Any cached data

# When deleting user account:
# - All CVs (which cascades to analyses)
# - All uploaded files
# - User record itself
```

### 6.4.3. New Files Structure

```
frontend/app/
+-- dashboard/
|   +-- page.tsx           # Enhanced dashboard
+-- cvs/
|   +-- page.tsx           # CV history list
|   +-- [cvId]/
|   |   +-- page.tsx       # CV detail (existing, add delete)
|   +-- upload/
|       +-- page.tsx       # Upload page (existing)
+-- profile/
    +-- page.tsx           # User profile

frontend/features/
+-- cv/
|   +-- components/
|       +-- CVHistoryList.tsx
|       +-- CVHistoryCard.tsx
|       +-- DeleteCVDialog.tsx
|       +-- CVDownloadButton.tsx
+-- profile/
    +-- components/
    |   +-- ProfileCard.tsx
    |   +-- UserStats.tsx
    |   +-- AccountActions.tsx
    |   +-- DeleteAccountDialog.tsx
    +-- actions.ts
```

---

## 6.5. User Stories

### Story 6.1: CV History List Page

**As a** Job Seeker,
**I want** to see all my uploaded CVs in one place,
**So that** I can track my CV versions and improvements.

#### Acceptance Criteria

1. Tao CV history page tai `/cvs`
2. Display list of all user's CVs
3. Each CV shows: filename, upload date, quality score
4. Sort by date (newest first, configurable)
5. Show CV count and pagination
6. Link to full analysis for each CV
7. Responsive card layout

---

### Story 6.2: CV Deletion Feature

**As a** Job Seeker,
**I want** to delete my CVs,
**So that** I can control my personal data.

#### Acceptance Criteria

1. Delete button on CV history list va detail page
2. Confirmation dialog with clear warning
3. List what will be deleted (file, analysis, skills data)
4. API endpoint deletes CV and all associated data
5. Delete file from storage
6. Show success message after deletion
7. Redirect to history list after delete from detail page
8. Audit log the deletion (optional)

---

### Story 6.3: CV Download Feature

**As a** Job Seeker,
**I want** to download my original CV,
**So that** I can access my files when needed.

#### Acceptance Criteria

1. Download button on CV history va detail page
2. API endpoint returns original file
3. Preserve original filename
4. Handle missing files gracefully (error message)
5. Track download count (optional)

---

### Story 6.4: Enhanced Dashboard

**As a** Job Seeker,
**I want** a comprehensive dashboard,
**So that** I can quickly access key information.

#### Acceptance Criteria

1. Welcome message voi user name
2. Quick action buttons (Upload CV, View History)
3. Recent CVs preview (last 3-5)
4. Overall stats (total CVs, average score)
5. Skill summary (top skills, recommendations)
6. Link to profile
7. Responsive layout

---

### Story 6.5: User Profile Page

**As a** Job Seeker,
**I want** to view and manage my profile,
**So that** I can control my account.

#### Acceptance Criteria

1. Tao profile page tai `/profile`
2. Display user info (email, member since)
3. Display statistics (CV count, scores)
4. Change password link/button
5. Account deletion option with confirmation
6. Avatar placeholder (actual upload optional)
7. Responsive design

---

### Story 6.6: User Statistics API

**As a** developer,
**I want** user statistics endpoint,
**So that** frontend can display user progress.

#### Acceptance Criteria

1. Tao `/api/v1/users/me/stats` endpoint
2. Return total CVs uploaded
3. Return average quality score
4. Return best quality score
5. Return total unique skills across all CVs
6. Return most common skills
7. Cache results for performance

---

### Story 6.7: Account Deletion Feature

**As a** Job Seeker,
**I want** to delete my account,
**So that** I can completely remove my data from the platform.

#### Acceptance Criteria

1. Delete account button in profile
2. Multi-step confirmation (type email to confirm)
3. API endpoint deletes all user data
4. Cascade delete: CVs, analyses, files
5. Logout user after deletion
6. Send confirmation email (optional)
7. 30-day recovery window (optional - future)

---

### Story 6.8: Loading States & Error Handling

**As a** Job Seeker,
**I want** clear feedback during operations,
**So that** I know what's happening.

#### Acceptance Criteria

1. Loading skeletons for CV list
2. Loading spinner for async actions
3. Progress indicator for file uploads
4. Clear error messages with actionable info
5. Toast notifications for success/error
6. Retry option for failed operations
7. Empty states for no data scenarios

---

## 6.6. Implementation Priority

| Priority | Story | Rationale |
|----------|-------|-----------|
| **P0 - Must Have** | 6.1 CV History List | Core navigation |
| **P0 - Must Have** | 6.2 CV Deletion | Data privacy requirement |
| **P0 - Must Have** | 6.4 Enhanced Dashboard | User experience |
| **P1 - Should Have** | 6.3 CV Download | User convenience |
| **P1 - Should Have** | 6.5 Profile Page | Account management |
| **P1 - Should Have** | 6.6 User Stats API | Dashboard data |
| **P2 - Nice to Have** | 6.7 Account Deletion | Full data control |
| **P2 - Nice to Have** | 6.8 Loading States | Polish |

---

## 6.7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Data not fully deleted | High | Low | Test cascade deletion thoroughly |
| File storage issues | Medium | Low | Error handling, fallback messages |
| Stats calculation slow | Low | Medium | Caching, async calculation |
| Accidental deletion | High | Low | Confirmation dialogs, clear warnings |

---

## 6.8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| CV list loads correctly | All CVs shown | Manual testing |
| Delete works end-to-end | Data fully removed | Database verification |
| Dashboard provides value | Key info visible | User feedback |
| Profile displays correctly | All info accurate | Manual testing |

---

## 6.9. Dependencies

| Story | Depends On |
|-------|------------|
| 6.1 CV History | Existing CV module (Epic 2) |
| 6.2 CV Deletion | 6.1 CV History |
| 6.3 CV Download | 6.1 CV History |
| 6.4 Dashboard | 6.1, 6.6 |
| 6.5 Profile | 6.6 User Stats |
| 6.6 User Stats | Existing CV data |
| 6.7 Account Deletion | 6.5 Profile |
| 6.8 Loading States | All frontend stories |
