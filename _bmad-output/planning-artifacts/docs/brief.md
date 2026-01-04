# Project Brief: AI-Powered Recruitment Platform

**Document Version:** 1.0  
**Date:** December 9, 2025  
**Project Type:** Graduation Thesis Project (DATN)  
**Status:** Active Development

---

## Executive Summary

The AI-Powered Recruitment Platform is a comprehensive digital solution designed to revolutionize the job matching process by leveraging artificial intelligence to bridge the gap between job seekers and employers. The platform addresses critical pain points in the recruitment ecosystem: job seekers struggle to optimize their CVs and find relevant opportunities, while recruiters face an overwhelming volume of applications with poor signal-to-noise ratio.

**Core Value Proposition:** Intelligent automation of CV analysis, job matching, and candidate screening powered by AI/RAG technology using local LLM models (Ollama).

---

## 1. Business Context

### 1.1 Problem Statement

**For Job Seekers:**
- Limited understanding of CV quality and ATS compatibility
- Difficulty identifying skill gaps for target positions
- Poor interview preparation and lack of feedback
- Time-consuming manual job searches across multiple platforms
- Uncertainty about job market positioning and career path

**For Recruiters/Hiring Managers:**
- High volume of irrelevant applications (low signal-to-noise)
- Semantic gap: missing qualified candidates due to keyword mismatch
- Manual screening is time-intensive and prone to bias
- Difficulty verifying candidate skills and experience
- Risk of losing top talent to competitors during slow hiring processes

**For the Industry:**
- Inefficient matching algorithms rely on exact keyword matching
- Lack of transparency in the application process
- Limited tools for skill validation and interview assessment
- No integrated workflow from CV submission to hiring decision

### 1.2 Market Opportunity

The recruitment technology market continues to grow as organizations seek efficiency and better candidate experiences. Key trends supporting this project:

- **AI Adoption in HR:** Growing acceptance of AI-assisted recruiting
- **Remote Work Era:** Increased need for digital-first recruitment tools
- **Skills-Based Hiring:** Shift from credentials to competency-based evaluation
- **Candidate Experience:** Job seekers expect transparency and feedback
- **Data Privacy:** Local LLM processing addresses data security concerns

---

## 2. Solution Overview

### 2.1 Product Vision

Create an intelligent recruitment ecosystem that empowers job seekers to present their best selves while enabling recruiters to discover talent efficiently through AI-powered semantic understanding and automated screening.

### 2.2 Key Features

#### **For Job Seekers (Candidates)**
1. **CV Analysis & Enhancement**
   - Upload CV (PDF/DOCX) with automatic parsing
   - Receive quality score (0-100) and actionable feedback
   - ATS-compatibility checks and formatting recommendations
   - Spelling and grammar detection
   - AI-powered rewriting of experience and summary sections
   - Job Description matching with keyword gap analysis

2. **Career Development Tools**
   - Career path suggestions based on current skills
   - Mock interview question generation
   - Personalized upskilling recommendations
   - CV version history and improvement tracking

3. **Job Discovery & Application**
   - Semantic job search (natural language queries)
   - Automated job recommendations
   - Email notification integration for new opportunities
   - Simplified application workflow

4. **Privacy & Data Control**
   - User-controlled data deletion
   - Transparent data usage policies

#### **For Recruiters/Hiring Managers**
1. **Intelligent Candidate Discovery**
   - Natural language search (e.g., "Developer skilled in Python and finance")
   - Semantic matching beyond keyword overlap
   - Upload JD for automatic candidate ranking
   - Hard filter definitions (degree, location, experience)

2. **AI-Assisted Screening**
   - Match score breakdown with detailed rationale
   - Access to candidate mock interview summaries
   - Skills verification badges/reports
   - Pipeline stage management (Screening → Interview → Offer)

3. **Workflow Automation**
   - Automated interview invitation emails
   - Candidate notes and internal feedback sharing
   - Integration-ready API design

#### **For Administrators**
1. **User & Content Management**
   - User monitoring and account management
   - Ban/suspend capabilities for policy violations
   - Content moderation (flagged CVs/JDs)

2. **AI Infrastructure Monitoring**
   - Real-time resource monitoring (GPU/RAM usage)
   - Model switching interface (e.g., Llama3 ↔ Mistral)
   - System prompt configuration per model
   - Inference latency tracking
   - Generation parameter adjustments (temperature, context window)

3. **Analytics & Reporting**
   - Key metrics dashboard (CVs parsed, matches made, DAU)
   - System logs and audit trails
   - Data export functionality

---

## 3. Technical Architecture

### 3.1 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16 (App Router) | Modern React framework with SSR/SSG capabilities |
| | Shadcn/ui + Tailwind CSS | Accessible component library and utility-first CSS |
| | TypeScript | Type safety and developer experience |
| | useActionState | Server Actions for form handling |
| **Backend** | Python 3.13 + FastAPI | High-performance async API framework |
| | SQLAlchemy 2.0 | Modern ORM with async support |
| | Alembic | Database migration management |
| | Pydantic | Data validation and settings management |
| **Database** | PostgreSQL | Robust relational database |
| **AI/ML** | Ollama (Local LLM) | Privacy-focused AI inference |
| | RAG (Retrieval-Augmented Generation) | Context-aware AI responses |
| **Authentication** | JWT + HttpOnly Cookies | Secure token-based auth with XSS protection |
| | Passlib + Bcrypt | Password hashing |
| **Email** | FastAPI-Mail | Transactional email delivery |
| **DevOps** | Asyncpg | Async PostgreSQL driver |

### 3.2 Architecture Patterns

**Backend Structure (Modular Architecture):**
```
backend/
├── app/
│   ├── core/           # Config, database, security
│   ├── modules/        # Feature modules
│   │   ├── auth/       # Authentication & authorization
│   │   ├── users/      # User management
│   │   ├── cvs/        # CV processing
│   │   └── jobs/       # Job management
│   ├── api/            # API route aggregation
│   ├── templates/      # Email templates
│   └── main.py         # Application entry point
├── alembic/            # Database migrations
└── requirements.txt
```

**Frontend Structure (Feature-Based):**
```
frontend/
├── app/
│   ├── (auth)/         # Auth route group
│   │   ├── login/
│   │   ├── register/
│   │   ├── forgot-password/
│   │   ├── reset-password/
│   │   └── verify-email/
│   └── dashboard/      # Protected routes
├── components/         # Reusable UI components
├── features/           # Feature-specific logic
│   └── auth/          # Auth forms, actions, types
├── services/          # API clients
└── lib/               # Utilities
```

### 3.3 Key Technical Decisions

1. **Local LLM (Ollama):** Ensures data privacy and reduces API costs
2. **HttpOnly Cookies:** Prevents XSS attacks on authentication tokens
3. **Modular Architecture:** Improves maintainability and team collaboration
4. **Server Actions:** Simplifies form handling with progressive enhancement
5. **Async/Await:** Enables high concurrency for AI processing

---

## 4. User Personas

### Persona 1: "The Proactive Job Seeker"
- **Demographics:** Fresh graduates to mid-level professionals
- **Goals:** Find relevant jobs, improve CV, prepare for interviews
- **Pain Points:** Black box applications, weak interview skills, unclear career paths
- **Success Metrics:** Higher callback rates, confident interviews, clear skill development plan

### Persona 2: "The Efficient Talent Seeker"
- **Demographics:** HR managers, technical recruiters, hiring managers
- **Goals:** Discover qualified candidates quickly, reduce time-to-hire
- **Pain Points:** Irrelevant applications, keyword-only search, slow screening
- **Success Metrics:** Reduced screening time, higher quality shortlists, faster hiring cycles

### Persona 3: "The Platform Guardian"
- **Demographics:** System administrators, DevOps engineers
- **Goals:** Maintain platform health, monitor performance, ensure data quality
- **Pain Points:** System abuse, unclear KPIs, manual data enrichment
- **Success Metrics:** High uptime, fast AI inference, clean user data, actionable insights

---

## 5. Minimum Viable Product (MVP) Scope

### Epic 1: Secure User Authentication ✓ (In Progress)
- User registration with email verification
- Secure login/logout with JWT + HttpOnly Cookies
- Password reset flow
- Token expiration and refresh
- Protected API endpoints

### Epic 2: AI-Powered CV Analysis (Core MVP)
- CV upload (PDF/DOCX support)
- Automatic parsing and extraction
- Quality score calculation (0-100)
- Summary generation
- Feedback on formatting, grammar, ATS compatibility

### Epic 3: AI-Powered Candidate Discovery (Core MVP)
- Job Description upload
- Semantic candidate ranking
- Natural language search interface
- Match score display with breakdown

### Epic 4: Admin Oversight (Supporting MVP)
- Resource monitoring dashboard (GPU/RAM, latency)
- System logs access
- Basic user management

### Post-MVP Features (Future Phases)
- Mock interview generation and assessment
- Email integration for job alerts
- Contract analysis tool
- Skills verification system
- Advanced analytics
- Mobile application

---

## 6. Success Metrics (KPIs)

### User Engagement
- Daily Active Users (DAU) / Monthly Active Users (MAU)
- CVs uploaded per user
- Search queries performed
- Time spent on platform

### Platform Performance
- CV parsing success rate (target: >95%)
- Average inference latency (target: <5 seconds)
- System uptime (target: >99%)
- API response time (target: <500ms p95)

### Business Impact
- Job seeker callback rate improvement
- Recruiter time-to-shortlist reduction
- Match accuracy (user feedback scores)
- User retention rate

---

## 7. Project Constraints & Risks

### Technical Constraints
- **GPU Resources:** Ollama requires significant compute for optimal performance
- **Model Selection:** Balance between accuracy and inference speed
- **Data Privacy:** Must process all data locally (no cloud AI APIs)

### Business Constraints
- **Thesis Timeline:** Must deliver MVP within academic deadlines
- **Budget:** Limited resources for infrastructure and third-party services
- **Data Scraping:** Cannot publicly deploy features using unauthorized data scraping

### Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|-----------|---------------------|
| AI model performance issues | High | Medium | Test multiple models; implement fallback strategies |
| CV parsing accuracy | High | Medium | Validate with diverse CV samples; iterative refinement |
| Scalability under load | Medium | High | Implement caching; async processing; database optimization |
| User adoption | High | Medium | Focus on UX; provide clear value demonstration |
| Data privacy concerns | High | Low | Emphasize local processing; transparent data policies |

---

## 8. Development Roadmap

### Phase 1: Foundation (Current)
- ✓ Project setup and architecture design
- ✓ Authentication system implementation
- ✓ Database schema and migrations
- ✓ Core API infrastructure
- 🔄 Frontend authentication flows

### Phase 2: Core MVP (Next)
- CV upload and parsing module
- AI integration with Ollama
- Quality scoring algorithm
- Basic semantic search
- JD upload and candidate ranking

### Phase 3: Enhancement
- User dashboard with analytics
- Admin monitoring interface
- Email notifications
- Advanced matching algorithms
- Feedback collection system

### Phase 4: Polish & Deployment
- Performance optimization
- Security hardening
- User acceptance testing
- Documentation completion
- Deployment setup

---

## 9. Stakeholders

### Primary Stakeholders
- **Student Developer:** Luong Hai Lam (Project Owner & Full Stack Developer)
- **Academic Advisor:** Thesis supervisor (guidance and evaluation)
- **Faculty Committee:** Đại Học Đông Á - Faculty of Information Technology

### Secondary Stakeholders
- **End Users:** Job seekers and recruiters (testing and feedback)
- **Technical Reviewers:** Faculty members evaluating technical implementation

---

## 10. Competitive Landscape

### Direct Competitors
- **LinkedIn:** Job matching, profile optimization suggestions
- **Indeed:** Resume builder, job search aggregation
- **Glassdoor:** Company reviews, salary insights
- **Resume.io / Zety:** CV building and templates

### Competitive Advantages
- **Local AI Processing:** Privacy-first approach vs. cloud-based competitors
- **Semantic Search:** Beyond keyword matching
- **Integrated Workflow:** All-in-one platform from CV improvement to hiring
- **Free & Open Architecture:** Academic project with potential for open-source release
- **Vietnamese Market Focus:** Localization and cultural relevance

### Competitive Disadvantages
- **Brand Recognition:** No established user base
- **Network Effects:** Smaller job/candidate pool vs. LinkedIn/Indeed
- **Resources:** Limited marketing budget and infrastructure
- **Features:** Mature competitors have more extensive tools

---

## 11. Next Steps

### Immediate Actions (Week 1-2)
1. Complete authentication flow testing (frontend + backend)
2. Design CV upload UI/UX
3. Set up Ollama development environment
4. Define CV parsing data model

### Short-term Goals (Month 1)
1. Implement CV upload and storage
2. Integrate Ollama for basic text analysis
3. Build quality scoring algorithm (v1)
4. Create simple admin dashboard

### Medium-term Goals (Month 2-3)
1. Deploy MVP to staging environment
2. Conduct user testing with 10-20 real users
3. Iterate based on feedback
4. Complete JD upload and matching feature
5. Prepare thesis documentation

---

## 12. Appendix

### A. References
- Project Brainstorming Document: `brain-storming-documentation.md`
- User Stories: `user_story.md`
- Technical Specifications: `tech.md`
- Presentation Notes: `presentation.md`

### B. Glossary
- **ATS:** Applicant Tracking System - software used by companies to filter CVs
- **RAG:** Retrieval-Augmented Generation - AI technique combining search and generation
- **JD:** Job Description
- **MVP:** Minimum Viable Product
- **Semantic Search:** Search based on meaning and context, not just keywords
- **DATN:** Đồ Án Tốt Nghiệp (Graduation Thesis Project)

### C. Contact Information
- **Project Repository:** `/home/luonghailam/Projects/datn`
- **University:** Đại Học Đông Á (Dong A University)
- **Department:** Khoa Công Nghệ Thông Tin (Faculty of Information Technology)

---

**Document End**

*This project brief is a living document and should be updated as the project evolves.*
