
# Project Tech & Requirements

## User Personas

### The "Proactive Job Seeker" (Candidate)

- **Primary Goal**: To find a highly relevant job that matches not just skills, but also practical needs like distance, salary, and benefits.
- **Key Frustrations**: The "black box" of applications, vague job posts, difficulty standing out, and personal limitations like interview skills.
- **Core Needs (Feature Drivers)**: AI-Powered Matching, AI-Powered CV Enhancement, Transparency, Employer Insights, Simplified Application.

### The "Efficient Talent Seeker" (Recruiter/Hiring Manager)

- **Primary Goals**: To find the right candidates quickly, manage postings efficiently, and reduce manual effort.
- **Key Frustrations**: Low Signal-to-Noise (irrelevant CVs), Semantic Gap (missing good candidates due to keyword differences), Lack of Validation (verifying skills), Speed (losing talent to competitors).
- **Core Needs (Feature Drivers)**: Tier 1 Automated Screening (Hard Filters), Tier 2 Semantic Search, Tier 3 AI-Powered Validation, Integrated Workflow.

### The "Platform Guardian" (Administrator)

- **Primary Goals**: Maintain platform health, monitor business growth, resolve user issues, and enrich the platform's dataset through data scraping.
- **Key Frustrations**: Dealing with platform abuse (spam, disputes), lack of visibility into KPIs, manual data entry to grow the employer pool.
- **Core Needs (Feature Drivers)**: Analytics Dashboard, User Management Tools, Content Moderation, Scraping Management Interface.

## Comprehensive User Stories (Backlog)

### Job Seeker User Stories

- As a Job Seeker, I want to upload my CV (PDF/DOCX) so that the system can parse and understand my professional profile.
- As a Job Seeker, I want to receive an overall score (e.g., 0-100) so that I can quickly gauge the quality of my current resume.
- As a Job Seeker, I want to get specific feedback on formatting and layout so that I can ensure my CV is ATS-friendly (Applicant Tracking System).
- As a Job Seeker, I want to identify spelling and grammatical errors so that my CV looks professional and polished.
- As a Job Seeker, I want to ask the AI questions about specific sections of my CV so that I can understand why a section is weak and how to rewrite it.
- As a Job Seeker, I want to input a specific Job Description (JD) so that the AI can compare my CV against it and calculate a "Matching Score".
- As a Job Seeker, I want to receive a "Keyword Gap" analysis based on a JD so that I know which technical keywords or skills I am missing and need to add.
- As a Job Seeker, I want the AI to rewrite my "Summary" or "Experience" bullet points so that they sound more impactful and action-oriented.
- As a Job Seeker, I want to get career path suggestions based on my current skills so that I can explore suitable roles I hadn't considered.
- As a Job Seeker, I want to generate mock interview questions based on my CV so that I can practice answering questions relevant to my actual experience.
- As a Job Seeker, I want to receive suggestions for upskilling (courses, certs) so that I can fill the skill gaps identified in the analysis phase.
- As a Job Seeker, I want to view my history of uploaded CVs and analyses so that I can track my improvements over time.
- As a Job Seeker, I want to delete my data from the system so that I can protect my privacy when I no longer need the service.

### Talent Seeker User Stories

- As a Talent Seeker, I want to define "Hard Filters" (e.g., Degree, Location, Years of Exp) so that the system automatically filters out applicants who don't meet minimum requirements.
- As a Talent Seeker, I want to search for candidates using Natural Language (e.g., "Developer rành Python và tài chính") so that I can find suitable profiles based on meaning/context, not just exact keywords (Semantic Search).
- As a Talent Seeker, I want to upload a specific Job Description (JD) so that the AI automatically ranks all available candidates based on their relevance to this JD.
- As a Talent Seeker, I want to view the "Match Score" breakdown of a candidate so that I can understand specifically why the AI recommends them (e.g., strong Tech stack, weak Soft skills).
- As a Talent Seeker, I want to access summaries/scores from the candidate's AI Mock Interview sessions so that I can pre-assess their communication skills and technical knowledge before scheduling a real meeting.
- As a Talent Seeker, I want to see a "Skills Verification" badge/report so that I know which claims in their CV have been validated by the system.
- As a Talent Seeker, I want to move candidates through pipeline stages (e.g., Screening -> Interviewing -> Offer) so that I can keep track of the hiring progress clearly.
- As a Talent Seeker, I want to send automated interview invitations via email so that I can schedule meetings efficiently without manual email composition.
- As a Talent Seeker, I want to add private notes to a candidate's profile so that I can share internal feedback with other hiring managers.

### Administrator User Stories

- As an Admin, I want to view a list of all Job Seekers and Talent Seekers so that I can monitor user growth and handle support requests.
- As an Admin, I want to ban or suspend specific accounts so that I can prevent spam, fraud, or abusive behavior on the platform.
- As an Admin, I want to review flagged content (CVs or JDs) so that I can remove inappropriate or malicious files uploaded to the system.
- As an Admin, I want to view real-time server resources (GPU/RAM usage) so that I can ensure Ollama is not crashing the server during high traffic.
- As an Admin, I want to switch active models (e.g., from Llama3 to Mistral) so that I can test which model gives better results for CV parsing without changing code.
- As an Admin, I want to input "System Prompts" separately for each model so that I can optimize instructions because different models behave differently.
- As an Admin, I want to adjust generation parameters (Temperature, Context Window) so that I can balance between creativity (for career advice) and precision (for CV extraction).
- As an Admin, I want to monitor Inference Latency (tốc độ phản hồi) so that I know if the current model is too heavy/slow for user experience.
- As an Admin, I want to view key metrics (Total CVs parsed, Matches made, Daily Active Users) so that I can evaluate the performance and success of the application.
- As an Admin, I want to export system logs or data reports so that I can perform offline analysis or auditing.

## Minimum Viable Product (MVP) Scope

### Epic 1: Secure User Authentication

- As a User, I want to Register and Login so that I can securely access my personal data.
- As an Admin, I want authentication tokens to be stored in HttpOnly Cookies to prevent XSS attacks.
- As an Admin, I want the system to reject API requests without a valid cookie.
- As an Admin, I want cookies to have an expiration time.
- As a User, I want to log out to securely terminate my session.
- (And all related technical stories for JWT and session management).

### Epic 2: AI-Powered CV Analysis & Feedback (for Job Seeker)

- As a Job Seeker, I want to upload my CV (PDF/DOCX) so that the system can parse and understand my professional profile.
- As a Job Seeker, I want to receive a brief Summary and an Initial Score (0-100) immediately after uploading, so that I know the system has successfully parsed and analyzed my profile.

### Epic 3: AI-Powered Candidate Discovery (for Talent Seeker)

- As a Talent Seeker, I want to upload a specific Job Description (JD) so that the AI automatically ranks all available candidates based on their relevance to this JD.
- As a Talent Seeker, I want to search for candidates using Natural Language (e.g., "Developer rành Python và tài chính") so that I can find suitable profiles based on meaning/context, not just exact keywords (Semantic Search).

### Epic 4: Admin Oversight

- A basic dashboard for the Admin to:
    - Monitor server resources (GPU/RAM) to ensure Ollama's stability.
    - Track inference latency to ensure the user experience is acceptable.
    - Access system logs for debugging the AI pipeline. (This combines Administrator stories: view real-time server resources, monitor Inference Latency, export system logs)



