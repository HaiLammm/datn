# DATN Brownfield Enhancement PRD

## Table of Contents

- [DATN Brownfield Enhancement PRD](#table-of-contents)
  - [1. Intro Project Analysis and Context](./1-intro-project-analysis-and-context.md)
    - [1.1. Existing Project Overview](./1-intro-project-analysis-and-context.md#11-existing-project-overview)
      - [1.1.1. Analysis Source](./1-intro-project-analysis-and-context.md#111-analysis-source)
      - [1.1.2. Current Project State](./1-intro-project-analysis-and-context.md#112-current-project-state)
    - [1.2. Available Documentation Analysis](./1-intro-project-analysis-and-context.md#12-available-documentation-analysis)
    - [1.3. Enhancement Scope Definition](./1-intro-project-analysis-and-context.md#13-enhancement-scope-definition)
      - [1.3.1. Enhancement Type](./1-intro-project-analysis-and-context.md#131-enhancement-type)
      - [1.3.2. Enhancement Description](./1-intro-project-analysis-and-context.md#132-enhancement-description)
      - [1.3.3. Impact Assessment](./1-intro-project-analysis-and-context.md#133-impact-assessment)
    - [1.4. Goals and Background Context](./1-intro-project-analysis-and-context.md#14-goals-and-background-context)
      - [1.4.1. Goals](./1-intro-project-analysis-and-context.md#141-goals)
      - [1.4.2. Background Context](./1-intro-project-analysis-and-context.md#142-background-context)
    - [1.5. Change Log](./1-intro-project-analysis-and-context.md#15-change-log)
  - [2. Requirements](./2-requirements.md)
    - [2.1. Functional Requirements](./2-requirements.md#21-functional-requirements)
    - [2.2. Non Functional Requirements](./2-requirements.md#22-non-functional-requirements)
    - [2.3. Compatibility Requirements](./2-requirements.md#23-compatibility-requirements)
  - [3. User Interface Enhancement Goals](./3-user-interface-enhancement-goals.md)
      - [3.1. Integration with Existing UI](./3-user-interface-enhancement-goals.md#31-integration-with-existing-ui)
      - [3.2. Modified/New Screens and Views](./3-user-interface-enhancement-goals.md#32-modifiednew-screens-and-views)
      - [3.3. UI Consistency Requirements](./3-user-interface-enhancement-goals.md#33-ui-consistency-requirements)
  - [4. Technical Constraints and Integration Requirements](./4-technical-constraints-and-integration-requirements.md)
      - [4.1. Existing Technology Stack](./4-technical-constraints-and-integration-requirements.md#41-existing-technology-stack)
      - [4.2. Integration Approach](./4-technical-constraints-and-integration-requirements.md#42-integration-approach)
      - [4.3. Code Organization and Standards](./4-technical-constraints-and-integration-requirements.md#43-code-organization-and-standards)
      - [4.4. Deployment and Operations](./4-technical-constraints-and-integration-requirements.md#44-deployment-and-operations)
      - [4.5. Risk Assessment and Mitigation](./4-technical-constraints-and-integration-requirements.md#45-risk-assessment-and-mitigation)

---

## Epic Overview

| Epic | Name | Status | Stories |
|------|------|--------|---------|
| **Epic 1** | Secure User Authentication | Done | (Completed before brownfield) |
| **Epic 2** | [AI-Powered CV Analysis](./2-cv-analysis-epic.md) | Done | 2.1 - 2.5 |
| **Epic 3** | [AI-Powered Candidate Discovery](./3-candidate-discovery-epic.md) | Planned | 3.1 - 3.7 |
| **Epic 4** | [Admin Oversight & Monitoring](./4-admin-oversight-epic.md) | Planned | 4.1 - 4.7 |
| **Epic 5** | [Hybrid Skill Scoring](./5-hybrid-skill-scoring-epic.md) | Done | 5.1 - 5.6 |
| **Epic 6** | [Job Seeker UX Enhancements](./6-job-seeker-ux-epic.md) | Planned | 6.1 - 6.8 |

---

## Epics Detail

### Epic 1: Secure User Authentication (Completed)

Authentication system implemented before brownfield documentation. Includes:
- User registration with email verification
- Secure login/logout with JWT + HttpOnly Cookies
- Password reset flow
- Token expiration and refresh
- Protected API endpoints

---

### Epic 2: AI-Powered CV Analysis (Done)

**File:** [2-cv-analysis-epic.md](./2-cv-analysis-epic.md)

CV upload, parsing, and AI-powered analysis features. Includes OCR support for scanned CVs and RAG integration for enhanced analysis accuracy.

**Completed Stories:**
- Story 2.1: CV Upload (was 1.1.story.md)
- Story 2.2: CV Analysis Results Display (was 1.2.story.md)
- Story 2.3: Advanced Preprocessing and OCR (was 2.1.story.md)
- Story 2.4: CV Deletion and Data Privacy (was 2.2.story.md)
- Story 2.5: RAG Integration with Vector Database (was 2.3.story.md)

---

### Epic 3: AI-Powered Candidate Discovery (Planned)

**File:** [3-candidate-discovery-epic.md](./3-candidate-discovery-epic.md)

JD upload, candidate ranking, and semantic search for Talent Seekers (Recruiters).

**Planned Stories:**
- Story 3.1: Job Description Module Foundation
- Story 3.2: JD Parsing & Skill Extraction
- Story 3.3: Candidate Ranking Engine
- Story 3.4: Semantic Candidate Search
- Story 3.5: JD Upload Frontend
- Story 3.6: Candidate Results Frontend
- Story 3.7: Semantic Search Frontend

---

### Epic 4: Admin Oversight & Monitoring (Planned)

**File:** [4-admin-oversight-epic.md](./4-admin-oversight-epic.md)

Admin dashboard, system monitoring, and user management.

**Planned Stories:**
- Story 4.1: Admin Role & Authorization
- Story 4.2: System Resource Monitoring API
- Story 4.3: AI Service Metrics API
- Story 4.4: System Logs API
- Story 4.5: User Management API
- Story 4.6: Admin Dashboard Frontend
- Story 4.7: User Management Frontend

---

### Epic 5: Hybrid Skill Scoring (Done)

**File:** [5-hybrid-skill-scoring-epic.md](./5-hybrid-skill-scoring-epic.md)

Enhanced skill extraction, normalization, and scoring with hybrid approach (LLM + NLP).

**Completed Stories:**
- Story 5.1: Skill Taxonomy & Data Foundation
- Story 5.2: Skill Extraction Service
- Story 5.3: Skill Normalization & Deduplication
- Story 5.4: Skill Weight & Scoring Algorithm
- Story 5.5: Skill-JD Matching API
- Story 5.6: Skill Display UI Components

---

### Epic 6: Job Seeker UX Enhancements (Planned)

**File:** [6-job-seeker-ux-epic.md](./6-job-seeker-ux-epic.md)

Enhanced user experience for Job Seekers including CV history, profile management, and improved feedback.

**Planned Stories:**
- Story 6.1: CV History List Page
- Story 6.2: CV Deletion Feature
- Story 6.3: CV Download Feature
- Story 6.4: Enhanced Dashboard
- Story 6.5: User Profile Page
- Story 6.6: User Statistics API
- Story 6.7: Account Deletion Feature
- Story 6.8: Loading States & Error Handling

---

## Story Mapping

### Existing Stories (in docs/stories/)

| Story File | Epic | New Story ID | Status |
|------------|------|--------------|--------|
| 1.1.story.md | Epic 2 | 2.1 | Done |
| 1.2.story.md | Epic 2 | 2.2 | Done |
| 2.1.story.md | Epic 2 | 2.3 | Done |
| 2.2.story.md | Epic 2 | 2.4 | Done |
| 2.3.story.md | Epic 2 | 2.5 | Done |
| 5.1.story.md | Epic 5 | 5.1 | Done |
| 5.2.story.md | Epic 5 | 5.2 | Done |
| 5.3.story.md | Epic 5 | 5.3 | Done |
| 5.4.story.md | Epic 5 | 5.4 | Done |
| 5.5.story.md | Epic 5 | 5.5 | Done |
| 5.6.story.md | Epic 5 | 5.6 | Done |

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-15 | 1.0 | Initial PRD index | John (PM) |
| 2025-12-17 | 2.0 | Restructured Epics to align with Project Brief | John (PM) |
