# AI-Powered Recruitment Platform: Brainstorming Documentation

This document summarizes the brainstorming session for the AI-Powered Recruitment Platform, outlining key user personas, their needs, initial user stories, and the Minimum Viable Product (MVP) scope.

## Project Overview
*   **Backend:** Python (FastAPI) + PostgreSQL
*   **Frontend:** Next.js 16 (App Router)
*   **Key Technologies:** Shadcn/ui + Tailwind CSS, useActionState, AI/RAG (Ollama)
*   **Core Value:** AI-powered analysis and matching capabilities (Semantic Search, CV Parsing).

## 1. User Personas

### 1.1. The "Proactive Job Seeker" (Candidate)
*   **Primary Goal:** To find a highly relevant job that matches not just skills, but also practical needs like distance, salary, and benefits.
*   **Key Frustrations:** The "black box" of applications, vague job posts, difficulty standing out, and personal limitations like interview skills.
*   **Core Needs (Feature Drivers):** AI-Powered Matching, AI-Powered CV Enhancement, Transparency, Employer Insights, Simplified Application.

### 1.2. The "Efficient Talent Seeker" (Recruiter/Hiring Manager)
*   **Primary Goals:** To find the *right* candidates quickly, manage postings efficiently, and reduce manual effort.
*   **Key Frustrations:** Low Signal-to-Noise (irrelevant CVs), Semantic Gap (missing good candidates due to keyword differences), Lack of Validation (verifying skills), Speed (losing talent to competitors).
*   **Core Needs (Feature Drivers):** Tier 1 Automated Screening (Hard Filters), Tier 2 Semantic Search, Tier 3 AI-Powered Validation, Integrated Workflow.

### 1.3. The "Platform Guardian" (Administrator)
*   **Primary Goals:** Maintain platform health, monitor business growth, resolve user issues, and enrich the platform's dataset through data scraping.
*   **Key Frustrations:** Dealing with platform abuse (spam, disputes), lack of visibility into KPIs, manual data entry to grow the employer pool.
*   **Core Needs (Feature Drivers):** Analytics Dashboard, User Management Tools, Content Moderation, Scraping Management Interface.

## 3. Minimum Viable Product (MVP) Scope

### Epic 1: Secure User Authentication
*   As a User, I want to Register and Login so that I can securely access my personal data.
*   As an Admin, I want authentication tokens to be stored in **HttpOnly Cookies** to prevent XSS attacks.
*   As an Admin, I want the system to reject API requests without a valid cookie.
*   As an Admin, I want cookies to have an expiration time.
*   As a User, I want to log out to securely terminate my session.
*   *(And all related technical stories for JWT and session management).*

### Epic 2: AI-Powered CV Analysis & Feedback (for Job Seeker)
*   As a Job Seeker, I want to **upload my CV** (PDF/DOCX) so that the system can parse and understand my professional profile.
*   As a Job Seeker, I want to receive a brief **Summary and an Initial Score (0-100)** immediately after uploading, so that I know the system has successfully parsed and analyzed my profile.

### Epic 3: AI-Powered Candidate Discovery (for Talent Seeker)
*   As a Talent Seeker, I want to **upload a specific Job Description (JD)** so that the AI automatically ranks all available candidates based on their relevance to this JD.
*   As a Talent Seeker, I want to **search for candidates using Natural Language** (e.g., "Developer rành Python và tài chính") so that I can find suitable profiles based on meaning/context, not just exact keywords (Semantic Search).

### Epic 4: Admin Oversight
*   A basic dashboard for the Admin to:
    *   Monitor server resources (GPU/RAM) to ensure Ollama's stability.
    *   Track inference latency to ensure the user experience is acceptable.
    *   Access system logs for debugging the AI pipeline.
    *(This combines Administrator stories: view real-time server resources, monitor Inference Latency, export system logs)*
