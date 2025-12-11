# 2. Requirements

## 2.1. Functional Requirements

*   **FR1:** The system shall allow job seekers to upload CVs in PDF and DOCX formats for parsing.
*   **FR2:** The system shall automatically parse uploaded CVs to extract relevant professional information.
*   **FR3:** The system shall generate a quality score (0-100) for an uploaded CV based on predefined criteria.
*   **FR4:** The system shall provide a summarized overview of the parsed CV content.
*   **FR5:** The system shall perform ATS-compatibility checks and offer formatting recommendations for uploaded CVs.
*   **FR6:** The system shall allow talent seekers to upload a Job Description (JD) for candidate matching.
*   **FR7:** The system shall automatically rank available candidates based on their relevance to an uploaded JD.
*   **FR8:** The system shall enable natural language search for candidates using semantic understanding.
*   **FR9:** The system shall display real-time server resource utilization (GPU/RAM) for AI infrastructure.
*   **FR10:** The system shall monitor and display AI inference latency.
*   **FR11:** The system shall provide access to system logs related to the AI pipeline.
*   **FR12:** The system shall integrate new CV analysis features into the existing user interface while maintaining consistency.
*   **FR13:** The system shall integrate new JD upload and candidate search features into the existing user interface while maintaining consistency.
*   **FR14:** The system shall allow job seekers to delete their uploaded CVs and associated data to ensure data privacy.
*   **FR15:** The system shall display a history list of uploaded CVs and their corresponding analysis results for the logged-in user.

## 2.2. Non Functional Requirements

*   **NFR1:** The CV parsing success rate shall be greater than 95%.
*   **NFR2:** The system shall provide immediate feedback (loading status) to the user upon submission, while the AI analysis processes asynchronously within a reasonable time (e.g., < 30 seconds).
*   **NFR3:** The API response time for critical endpoints (e.g., CV upload, JD upload) shall be under 500ms for 95% of requests.
*   **NFR4:** The system shall maintain the established security controls (e.g., HttpOnly cookies, bcrypt hashing, JWT validation) for all new features.
*   **NFR5:** All processing of sensitive user data, particularly CV and JD content, shall be performed locally using the Ollama LLM to ensure data privacy.
*   **NFR6:** The system shall be capable of handling a growing volume of CV uploads, JD uploads, and AI processing requests.
*   **NFR7:** The system shall handle concurrent AI processing requests using an asynchronous task queue to prevent server overload.
*   **NFR8:** The user interfaces for CV analysis and candidate discovery shall be intuitive and user-friendly.
*   **NFR9:** User feedback mechanisms shall be incorporated to gather insights for continuous UI/UX improvement.
*   **NFR10:** The system shall aim for a minimum uptime of 99%.
*   **NFR11:** Robust error handling and logging mechanisms shall be implemented for all AI processing operations.
*   **NFR12:** All new code for this enhancement shall conform to the project's modular architecture, coding standards, and type-hinting guidelines.

## 2.3. Compatibility Requirements

*   **CR1: Existing API Compatibility:** New API endpoints and services for CV analysis and job matching shall seamlessly integrate with the existing FastAPI API structure, authentication mechanisms, and response formats, specifically under `/api/v1`.
*   **CR2: Database Schema Compatibility:** New database tables for CVs, jobs, and analysis results shall be designed to integrate with the existing PostgreSQL `users` table without breaking existing user data relationships or data integrity.
*   **CR3: UI/UX Consistency:** All new and modified user interface components shall adhere strictly to the established design system (Shadcn/ui, Tailwind CSS, specific color palette, Be Vietnam Pro font) to ensure a cohesive and consistent user experience.
*   **CR4: Integration Compatibility:** The integration of Ollama for AI processing shall be robust and not interfere with the performance or stability of existing backend services.
*   **CR5: System Environment:** The system shall support deployment on Linux environments (Ubuntu 20.04+) or Windows via WSL2 to ensure compatibility with Ollama.
*   **CR6: Hardware Requirements:** The system shall specify minimum hardware specifications for hosting the local LLM (Recommended: 16GB RAM, Dedicated NVIDIA GPU with 6GB+ VRAM) to meet the performance targets.
