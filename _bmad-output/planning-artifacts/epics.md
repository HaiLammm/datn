---
stepsCompleted: [1, 2, 3]
inputDocuments: ["/home/luonghailam/Projects/datn/_bmad-output/planning-artifacts/prd.md", "/home/luonghailam/Projects/datn/_bmad-output/planning-artifacts/ux-design-specification.md", "_bmad-output/planning-artifacts/architecture/api-specification.md", "_bmad-output/planning-artifacts/architecture/appendix-useful-commands-and-scripts.md", "_bmad-output/planning-artifacts/architecture/backend-architecture.md", "_bmad-output/planning-artifacts/architecture/checklist-results-report.md", "_bmad-output/planning-artifacts/architecture/coding-standards.md", "_bmad-output/planning-artifacts/architecture/components.md", "_bmad-output/planning-artifacts/architecture/core-workflows.md", "_bmad-output/planning-artifacts/architecture/data-models-and-apis.md", "_bmad-output/planning-artifacts/architecture/data-models.md", "_bmad-output/planning-artifacts/architecture/database-schema.md", "_bmad-output/planning-artifacts/architecture/deployment-architecture.md", "_bmad-output/planning-artifacts/architecture/development-and-deployment.md", "_bmad-output/planning-artifacts/architecture/development-workflow.md", "_bmad-output/planning-artifacts/architecture/error-handling-strategy.md", "_bmad-output/planning-artifacts/architecture/external-apis.md", "_bmad-output/planning-artifacts/architecture/frontend-architecture.md", "_bmad-output/planning-artifacts/architecture/high-level-architecture.md", "_bmad-output/planning-artifacts/architecture/if-enhancement-prd-provided-impact-analysis.md", "_bmad-output/planning-artifacts/architecture/index.md", "_bmad-output/planning-artifacts/architecture/integration-points-and-external-dependencies.md", "_bmad-output/planning-artifacts/architecture/introduction.md", "_bmad-output/planning-artifacts/architecture/monitoring-and-observability.md", "_bmad-output/planning-artifacts/architecture/quick-reference-key-files-and-entry-points.md", "_bmad-output/planning-artifacts/architecture/security-and-performance.md", "_bmad-output/planning-artifacts/architecture/source-tree-and-module-organization.md", "_bmad-output/planning-artifacts/architecture/source-tree.md", "_bmad-output/planning-artifacts/architecture/tech-stack.md", "_bmad-output/planning-artifacts/architecture/technical-debt-and-known-issues.md", "_bmad-output/planning-artifacts/architecture/testing-reality.md", "_bmad-output/planning-artifacts/architecture/testing-strategy.md"]
---

# datn - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for {{project_name}}, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

- **FR1:** A user can register for an account with the role of 'Job Seeker' or 'Recruiter'.
- **FR2:** A user can log in with an email and password to receive a secure authentication cookie (HttpOnly).
- **FR3:** An authenticated user can view their personal information (email, date joined).
- **FR4:** An authenticated user can change their password.
- **FR5:** An authenticated user can delete their account and all related data.
- **FR6:** A job seeker can upload a CV file (PDF, DOCX format).
- **FR7:** A job seeker can view a list of all their uploaded CVs.
- **FR8:** A job seeker can view the detailed analysis results for a specific CV.
- **FR9:** A job seeker can delete a specific CV and its related analysis data.
- **FR10:** A job seeker can download the original file of an uploaded CV.
- **FR11:** A job seeker can control the public visibility status (public/private) for their CV.
- **FR12:** The system can analyze an uploaded CV to extract text and skills.
- **FR13:** The system can provide a detailed quality score and improvement feedback for a CV.
- **FR14:** A job seeker can set up a virtual AI interview room for a specific job description or role.
- **FR15:** A job seeker can interact with the interview AI using voice.
- **FR16:** A job seeker can receive a detailed performance report after an AI interview session.
- **FR17:** A job seeker can view the history of their AI interview sessions.
- **FR18:** A recruiter can upload a Job Description (JD).
- **FR19:** The system can analyze an uploaded JD to extract requirements.
- **FR20:** A recruiter can view a list of all their uploaded JDs.
- **FR21:** A recruiter can view a list of ranked candidates suitable for a specific JD.
- **FR22:** A recruiter can search for candidates using natural language queries.
- **FR23:** A recruiter can create and manage "collections" of candidates for current or future roles.
- **FR24:** A recruiter can view the public CV analysis and AI interview results of a candidate.
- **FR25:** A recruiter can initiate a real-time chat with a candidate.
- **FR26:** A candidate can receive and reply to real-time messages from a recruiter.
- **FR27:** A user can view a list of all their conversations.
- **FR28:** An administrator can view a monitoring dashboard with system health metrics (GPU, RAM, latency).
- **FR29:** An administrator can view system logs.
- **FR30:** An administrator can manage users (view, filter, suspend).
- **FR31:** An administrator can manage content (view and hide job postings).

### NonFunctional Requirements

- **NFR1.1 (General Responsiveness):** The system should provide timely feedback for user interactions.
- **NFR1.2 (Real-time Chat):** Chat messages should be sent and received almost instantly.
- **NFR2.1 (Data Protection):** All personal information must be protected from unauthorized access.
- **NFR2.2 (Role-Based Access Control):** The system must strictly adhere to the role-based permission model.
- **NFR2.3 (Attack Protection):** The system must be resistant to basic DoS attacks.
- **NFR2.4 (Encryption):** Sensitive data must be encrypted.
- **NFR3.1 (Concurrent Users):** The system must support over 100 concurrent users.
- **NFR3.2 (Data Loss):** The system must not cause data loss.
- **NFR4.1 (Basic Accessibility):** The system will adhere to basic accessibility principles.
- **NFR5.1 (Ollama LLM):** The system must integrate seamlessly with the Ollama LLM.
- **NFR5.2 (Email SMTP):** The system must integrate with an Email SMTP service.
- **NFR5.3 (Integration Reliability):** Integrations must be highly reliable.
- **NFR6.1 (Data Integrity):** User data must be preserved.
- **NFR6.2 (Uptime):** Core functions must have at least 99% uptime.
- **NFR6.3 (Resilience):** The system must be resilient to non-critical errors.

### Additional Requirements

- **UXR1: Responsive Design:** Fully responsive web application.
- **UXR2: Device Feature Integration:** Utilize microphone and browser notifications.
- **UXR3: Real-time Updates:** UI must support real-time updates for chat.
- **UXR4: Accessibility:** Comply with WCAG AA standards.
- **UXR5: Intuitive AI Integration:** AI features must be natural and easy to understand.
- **UXR6: Voice UI:** Explore voice interactions for the AI interview room.
- **UXR7: Data Visualization:** Intuitive dashboards and reports for AI data.
- **UXR8: User Control over Data:** Clear control over data visibility.
- **AR1: API Versioning:** API must be versioned with `/api/v1`.
- **AR2: Authentication:** Protected endpoints use `CookieAuth`.
- **AR3: Data Format:** API uses JSON; `multipart/form-data` for uploads.
- **AR4: Error Response:** Errors returned with a `detail` field.
- **AR5: CV Endpoints:** Endpoints for CV CRUD operations.
- **AR6: JD Endpoints:** Endpoint for JD upload.
- **AR7: Candidate Matching:** Endpoint to get ranked candidates.
- **AR8: Semantic Search:** Endpoint for semantic candidate search.
- **AR9: Modular Architecture:** Backend features organized into modules.
- **AR10: Service Layer:** Separate business logic into a service layer.
- **AR11: Background Tasks:** AI analysis in background tasks.
- **AR12: Database Schema:** Tables for `users`, `cvs`, `job_descriptions`.
- **AR13: Vector Storage:** Use `pgvector` for embeddings (dimension 768).
- **AR14: Role-Based Access Control (RBAC):** `job_seeker`, `recruiter`, `admin` roles with guards.
- **AR15: File Storage:** Files saved to local disk.
- **AR16: Feature-First Architecture:** Frontend code organized by business features.
- **AR17: Server Actions:** Use Next.js Server Actions for mutations.
- **AR18: Form Handling:** Use `react-hook-form`, `Zod`, and `useActionState`.
- **AR19: Protected Routes:** Use Layout Guards for RBAC on routes.
- **AR20: API Service Layer:** Centralized API interactions in `/services`.
- **AR21: `withCredentials`:** `axios` client configured with `withCredentials: true`.

### FR Coverage Map

FR1: Epic 1 - Người dùng có thể đăng ký tài khoản.
FR2: Epic 1 - Người dùng có thể đăng nhập.
FR3: Epic 1 - Người dùng có thể xem thông tin cá nhân.
FR4: Epic 1 - Người dùng có thể thay đổi mật khẩu.
FR5: Epic 1 - Người dùng có thể xóa tài khoản.
FR6: Epic 2 - Người tìm việc có thể tải lên CV.
FR7: Epic 2 - Người tìm việc có thể xem danh sách CV đã tải lên.
FR8: Epic 2 - Người tìm việc có thể xem kết quả phân tích CV.
FR9: Epic 2 - Người tìm việc có thể xóa CV.
FR10: Epic 2 - Người tìm việc có thể tải xuống CV gốc.
FR11: Epic 2 - Người tìm việc có thể kiểm soát hiển thị công khai CV.
FR12: Epic 2 - Hệ thống có thể phân tích CV trích xuất văn bản và kỹ năng.
FR13: Epic 2 - Hệ thống có thể cung cấp điểm chất lượng và phản hồi cải thiện cho CV.
FR14: Epic 3 - Người tìm việc có thể thiết lập phòng phỏng vấn AI ảo.
FR15: Epic 3 - Người tìm việc có thể tương tác với AI phỏng vấn bằng giọng nói.
FR16: Epic 3 - Người tìm việc có thể nhận báo cáo hiệu suất sau phỏng vấn AI.
FR17: Epic 3 - Người tìm việc có thể xem lịch sử các buổi phỏng vấn AI.
FR18: Epic 4 - Nhà tuyển dụng có thể tải lên Mô tả Công việc (JD).
FR19: Epic 4 - Hệ thống có thể phân tích JD.
FR20: Epic 4 - Nhà tuyển dụng có thể xem danh sách JD đã tải lên.
FR21: Epic 4 - Nhà tuyển dụng có thể xem danh sách ứng viên đã xếp hạng.
FR22: Epic 4 - Nhà tuyển dụng có thể tìm kiếm ứng viên bằng truy vấn ngôn ngữ tự nhiên.
FR23: Epic 4 - Nhà tuyển dụng có thể tạo và quản lý "bộ sưu tập" ứng viên.
FR24: Epic 4 - Nhà tuyển dụng có thể xem phân tích CV và kết quả phỏng vấn AI công khai của ứng viên.
FR25: Epic 5 - Nhà tuyển dụng có thể bắt đầu cuộc trò chuyện thời gian thực với ứng viên.
FR26: Epic 5 - Ứng viên có thể nhận và trả lời tin nhắn thời gian thực.
FR27: Epic 5 - Người dùng có thể xem danh sách tất cả các cuộc trò chuyện.
FR28: Epic 6 - Quản trị viên có thể xem dashboard giám sát.
FR29: Epic 6 - Quản trị viên có thể xem log hệ thống.
FR30: Epic 6 - Quản trị viên có thể quản lý người dùng.
FR31: Epic 6 - Quản trị viên có thể quản lý nội dung.

## Epic List

### Epic 1: Nền tảng Xác thực và Quản lý Người dùng (User Authentication & Profile Foundation)
**Mục tiêu:** Cung cấp một hệ thống đăng ký, đăng nhập và quản lý tài khoản an toàn, tạo nền tảng cho tất cả các tính năng khác.
**FRs bao gồm:** FR1, FR2, FR3, FR4, FR5

### Epic 2: Phân tích & Quản lý CV bằng AI (AI-Powered CV Analysis & Management)
**Mục tiêu:** Cho phép người tìm việc tải lên, quản lý, và nhận phân tích chi tiết về CV của họ để cải thiện hồ sơ.
**FRs bao gồm:** FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR13

### Story 2.1: Tải lên CV (CV Upload)
As a người tìm việc,
I want để tải lên tệp CV của mình (định dạng PDF, DOCX),
So that hệ thống có thể phân tích và hiểu hồ sơ chuyên môn của tôi.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập, **When** tôi chọn một tệp CV hợp lệ (PDF/DOCX) và tải lên, **Then** tệp CV được lưu trữ an toàn và quá trình phân tích AI được bắt đầu trong nền. (Covers FR6, AR11, AR15)
*   **Given** tôi chọn một tệp không hợp lệ (không phải PDF/DOCX), **When** tôi cố gắng tải lên, **Then** hệ thống hiển thị thông báo lỗi.
*   **Given** tôi không phải chủ sở hữu hợp lệ, **When** tôi cố gắng tải lên, **Then** hệ thống từ chối yêu cầu và hiển thị lỗi.

### Story 2.2: Xem & Quản lý Danh sách CV (View & Manage CV List)
As a người tìm việc,
I want để xem danh sách tất cả các CV đã tải lên của mình với trạng thái phân tích,
So that tôi có thể theo dõi các phiên bản CV và biết khi nào kết quả phân tích sẵn sàng.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập và có các CV đã tải lên, **When** tôi truy cập trang danh sách CV, **Then** tôi thấy danh sách các CV với tên tệp, ngày tải lên và trạng thái phân tích (Đang chờ, Đang xử lý, Hoàn thành, Thất bại). (Covers FR7)
*   **Given** phân tích CV đang diễn ra, **When** tôi xem danh sách CV, **Then** trạng thái phân tích được cập nhật tự động mà không cần tải lại trang. (Covers NFR1.1)
*   **Given** không có CV nào được tải lên, **When** tôi truy cập trang danh sách CV, **Then** hệ thống hiển thị thông báo "Chưa có CV nào được tải lên".
*   **And** danh sách CV được phân trang (pagination) nếu có nhiều CV.

### Story 2.3: Xem Chi tiết Phân tích CV (View Detailed CV Analysis)
As a người tìm việc,
I want để xem kết quả phân tích chi tiết của một CV,
So that tôi có thể hiểu được điểm mạnh, các lĩnh vực cần cải thiện và nhận được phản hồi hữu ích.
**Acceptance Criteria:**
*   **Given** tôi đã tải lên một CV và quá trình phân tích hoàn tất, **When** tôi truy cập trang chi tiết phân tích của CV đó, **Then** tôi thấy tổng quan chất lượng, phân tích kỹ năng, kinh nghiệm và phản hồi ATS. (Covers FR8, FR12, FR13)
*   **Given** quá trình phân tích vẫn đang diễn ra, **When** tôi truy cập trang chi tiết, **Then** hệ thống hiển thị trạng thái tải và cập nhật tự động khi phân tích hoàn tất. (Covers NFR1.1)
*   **Given** quá trình phân tích thất bại, **When** tôi truy cập trang chi tiết, **Then** hệ thống hiển thị thông báo lỗi và tùy chọn thử lại.

### Story 2.4: Tải xuống & Xóa CV (Download & Delete CV)
As a người tìm việc,
I want để tải xuống tệp CV gốc của mình và xóa bất kỳ CV nào đã tải lên,
So that tôi có thể truy cập các tệp của mình khi cần và kiểm soát dữ liệu cá nhân.
**Acceptance Criteria:**
*   **Given** tôi đã tải lên một CV, **When** tôi yêu cầu tải xuống tệp CV gốc, **Then** hệ thống cung cấp tệp để tải xuống với tên tệp gốc. (Covers FR10, NFR6.1)
*   **Given** tôi muốn xóa một CV, **When** tôi yêu cầu xóa và xác nhận, **Then** CV đó và tất cả dữ liệu phân tích liên quan bị xóa vĩnh viễn khỏi hệ thống. (Covers FR9, NFR2.1, NFR3.2, NFR6.1)
*   **And** tôi không thể xóa CV của người dùng khác.

### Story 2.5: Kiểm soát Quyền riêng tư CV (CV Privacy Control)
As a người tìm việc,
I want để kiểm soát trạng thái hiển thị công khai (public/private) của CV của mình,
So that tôi có thể chọn chia sẻ chi tiết CV với nhà tuyển dụng hoặc duy trì quyền riêng tư.
**Acceptance Criteria:**
*   **Given** tôi đã tải lên một CV, **When** tôi thay đổi trạng thái hiển thị của CV (công khai/riêng tư), **Then** trạng thái mới được lưu trữ và phản ánh ngay lập tức. (Covers FR11, UXR8)
*   **Given** một nhà tuyển dụng tìm thấy hồ sơ của tôi, **When** CV của tôi là riêng tư, **Then** nhà tuyển dụng không thể xem chi tiết phân tích CV đầy đủ của tôi. (Covers NFR2.2)

### Epic 8: Phòng phỏng vấn AI ảo (Virtual AI Interview Room) 🚧 IN PROGRESS
**Mục tiêu:** Cung cấp một môi trường để ứng viên luyện tập phỏng vấn với AI, nhận phản hồi và theo dõi sự tiến bộ.
**FRs bao gồm:** FR14, FR15, FR16, FR17
**Status:** AI Sub-Agents Implementation Completed (January 7, 2026)
**Tech Stack:** Ollama (local), Llama-3.2-3B-Instruct, Qwen2.5-1.5B-Instruct, Python agents, FastAPI backend integration

#### AI Sub-Agents Architecture ✅ COMPLETED

**Implementation Approach:** Simple Agents + Database-managed context (not Expert Agents with memory)
- **Rationale:** Better scalability, no concurrency issues, single source of truth (PostgreSQL)
- **Performance:** DB overhead (~100-200ms) negligible vs inference time (~2-4s)

**3 Production AI Sub-Agents:**

1. **QuestionCraft AI** ❓ (Question Generator Agent)
   - **Model:** Llama-3.2-3B-Instruct-FP16
   - **Function:** Generate 10-15 interview questions from Job Description + CV
   - **Features:**
     - Level-appropriate questions (Junior/Middle/Senior)
     - 60-20-20 distribution (Technical-Behavioral-Situational)
     - Scenario-based questions referencing actual JD/CV content
     - JSON output with evaluation criteria for each question
   - **Performance Target:** < 5s latency (P95)
   - **Files:** `_sub-agents/agents/question_generator.py`, `configs/question_generator_config.json`, `prompts/question_generator_prompt.txt`

2. **DialogFlow AI** 💬 (Conversation Agent)
   - **Model:** Qwen2.5-1.5B-Instruct-FP16
   - **Function:** Manage interview conversation flow, evaluate answers per-turn
   - **Features:**
     - Real-time answer evaluation (Technical, Communication, Depth dimensions)
     - Intelligent next action decision (continue/follow-up/next_question/end)
     - Natural, encouraging conversation tone
     - Context-aware follow-up questions
   - **Performance Target:** < 3s latency per turn (P95)
   - **Files:** `_sub-agents/agents/conversation_agent.py`, `configs/conversation_agent_config.json`, `prompts/conversation_agent_prompt.txt`

3. **EvalMaster AI** 📊 (Performance Evaluator Agent)
   - **Model:** Llama-3.2-3B-Instruct-FP16
   - **Function:** Comprehensive interview evaluation with detailed report
   - **Features:**
     - 3-dimension scoring: Technical (50%), Communication (25%), Behavioral (25%)
     - Evidence-based analysis with specific quotes from transcript
     - Hiring recommendation (Strong Hire/Hire/Consider/No Hire)
     - Actionable feedback for both hiring decision and candidate development
   - **Performance Target:** < 8s latency (P95)
   - **Files:** `_sub-agents/agents/performance_evaluator.py`, `configs/performance_evaluator_config.json`, `prompts/performance_evaluator_prompt.txt`

**Deliverables Completed (24 files):**
- ✅ 3 System Prompts (comprehensive, Vietnamese-supported)
- ✅ 3 JSON Configuration files (model parameters, quality settings)
- ✅ 4 Python implementation files (base class + 3 agents with full error handling)
- ✅ 3 API request templates with examples
- ✅ 4 Documentation files (README, INTEGRATION_GUIDE, TESTING_GUIDE, PROMPT_TUNING)
- ✅ 3 Sample data files (JDs, CVs, interview transcripts)
- ✅ 4 Test files (conftest, base tests, question generator tests, test README)

**Directory Structure:**
```
_sub-agents/
├── agents/          # Python implementations
├── configs/         # JSON configurations
├── prompts/         # System prompts
├── api_examples/    # API request templates
├── samples/         # Test data
├── tests/           # Unit & integration tests
└── *.md            # Documentation
```

**Database Schema Extensions:**
- `interview_sessions` - Track interview sessions
- `interview_questions` - Store generated questions
- `interview_turns` - Record conversation history with per-turn evaluations
- `interview_evaluations` - Final comprehensive evaluation reports
- `agent_call_logs` - Monitor agent performance and errors

**Integration Status:**
- ✅ Agents implemented and ready
- ✅ Database schema designed
- 🚧 Backend service layer (pending)
- 🚧 FastAPI endpoints (pending)
- 🚧 Frontend UI (pending)

**Documentation:**
- Main: `_sub-agents/README.md` - Architecture, quick start, troubleshooting
- Integration: `_sub-agents/INTEGRATION_GUIDE.md` - Backend integration, DB schema, service layer
- Testing: `_sub-agents/TESTING_GUIDE.md` - Test strategy, quality metrics, CI/CD
- Customization: `_sub-agents/PROMPT_TUNING.md` - Prompt engineering best practices

### Story 8.1: Thiết lập Phòng Phỏng vấn Ảo (Virtual Interview Room Setup) 🚧 IN PROGRESS
As a người tìm việc,
I want để tạo một phòng phỏng vấn ảo cho một vị trí công việc cụ thể hoặc sử dụng CV đã tải lên,
So that AI có thể tạo ra các câu hỏi phỏng vấn phù hợp và cá nhân hóa.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập, **When** tôi cung cấp mô tả công việc hoặc chọn một CV đã tải lên, **Then** hệ thống tạo một phiên phỏng vấn mới với các câu hỏi phỏng vấn được cá nhân hóa bởi AI. (Covers FR14)
*   **Given** tôi không cung cấp đủ thông tin, **When** tôi cố gắng tạo phòng phỏng vấn, **Then** hệ thống yêu cầu bổ sung thông tin hoặc đề xuất các lựa chọn mặc định.
*   **And** tôi có thể xem trước các chủ đề hoặc loại câu hỏi sẽ được hỏi.
*   **And** tôi có thể thiết lập các thông số cơ bản cho buổi phỏng vấn (ví dụ: thời lượng, số lượng câu hỏi, độ khó).

**Implementation Details:**
- **Backend:** QuestionService calls QuestionCraft AI agent
- **API Endpoint:** `POST /api/v1/interviews/generate-questions`
- **Input:** `job_description`, `cv_content`, `position_level`, `num_questions`, `focus_areas` (optional)
- **Output:** JSON array of 10-15 questions with evaluation criteria
- **Database:** Questions saved to `interview_questions` table
- **Agent:** `QuestionGeneratorAgent` (Llama-3.2-3B, ~4s latency)

### Story 8.2: Tương tác Giọng nói với AI Phỏng vấn (Voice Interaction with AI Interviewer) 🚧 IN PROGRESS
As a người tìm việc,
I want để tương tác với AI phỏng vấn bằng giọng nói và nhận phản hồi bằng giọng nói,
So that trải nghiệm phỏng vấn chân thực và hiệu quả hơn.
**Acceptance Criteria:**
*   **Given** tôi đang trong phòng phỏng vấn ảo, **When** tôi sử dụng microphone để trả lời câu hỏi của AI, **Then** hệ thống chuyển đổi giọng nói của tôi thành văn bản và AI phân tích câu trả lời. (Covers FR15, UXR6)
*   **Given** AI đã phân tích câu trả lời của tôi, **When** tôi chờ đợi phản hồi, **Then** AI tạo ra phản hồi bằng văn bản và hệ thống chuyển đổi thành giọng nói để tôi nghe. (Covers FR15)
*   **Given** tôi gặp sự cố với microphone hoặc kết nối, **When** tôi đang tương tác, **Then** hệ thống hiển thị thông báo lỗi và đề xuất giải pháp.
*   **And** tất cả các tương tác (câu hỏi AI, câu trả lời của tôi) được ghi lại để xem xét sau này. (Covers NFR2.1, NFR6.1)

**Implementation Details:**
- **Backend:** ConversationService calls DialogFlow AI agent
- **API Endpoint:** `POST /api/v1/interviews/process-turn`
- **Input:** `interview_id`, `current_question`, `candidate_answer` (text from voice-to-text), `conversation_history`
- **Output:** 
  - `turn_evaluation`: Per-turn scores (Technical, Communication, Depth, Overall)
  - `next_action`: Action type + AI response + follow-up question (if needed)
  - `context_update`: Topics covered, follow-up depth, turn count
- **Database:** Each turn saved to `interview_turns` table with evaluations
- **Agent:** `ConversationAgent` (Qwen2.5-1.5B, ~3s latency per turn)
- **Frontend:** Voice-to-text (Web Speech API), text-to-speech for AI responses

### Story 8.3: Báo cáo Đánh giá Hiệu suất Phỏng vấn (Interview Performance Report) 🚧 IN PROGRESS
As a người tìm việc,
I want để nhận báo cáo đánh giá chi tiết về hiệu suất của mình sau buổi phỏng vấn,
So that tôi có thể học hỏi từ những sai lầm và cải thiện kỹ năng phỏng vấn của mình.
**Acceptance Criteria:**
*   **Given** tôi đã hoàn thành một buổi phỏng vấn ảo, **When** tôi truy cập báo cáo đánh giá, **Then** tôi thấy điểm tổng thể, điểm mạnh, điểm yếu và gợi ý cải thiện cụ thể. (Covers FR16)
*   **Given** tôi xem lại báo cáo, **When** tôi nhấp vào một câu hỏi cụ thể, **Then** tôi có thể xem lại câu hỏi và câu trả lời của mình (văn bản và âm thanh nếu có).
*   **And** báo cáo được lưu trữ an toàn và chỉ tôi mới có thể truy cập.

**Implementation Details:**
- **Backend:** EvaluationService calls EvalMaster AI agent
- **API Endpoint:** `POST /api/v1/interviews/evaluate`
- **Input:** 
  - `interview_id`, `candidate_info`
  - `interview_transcript`: Full conversation history
  - `questions_asked`: All questions with metadata
  - `turn_evaluations`: Per-turn scores from DialogFlow AI
  - `interview_duration_minutes`
- **Output:**
  - `overall_evaluation`: Final score (0-10), grade, hiring recommendation
  - `dimension_scores`: Technical (50%), Communication (25%), Behavioral (25%) with sub-scores and evidence
  - `detailed_analysis`: Key strengths, areas for improvement, notable moments, red flags
  - `recommendations`: Hiring decision, reasoning, role fit, onboarding suggestions, development areas
- **Database:** Report saved to `interview_evaluations` table
- **Agent:** `PerformanceEvaluatorAgent` (Llama-3.2-3B, ~6s latency)
- **Frontend:** Display comprehensive report with charts, dimension breakdown, evidence citations

### Story 8.4: Lịch sử Buổi Phỏng vấn (Interview History) 🚧 IN PROGRESS
As a người tìm việc,
I want để xem lại lịch sử các buổi phỏng vấn ảo đã thực hiện,
So that tôi có thể theo dõi sự tiến bộ của mình theo thời gian và chuẩn bị tốt hơn cho các buổi phỏng vấn thực tế.
**Acceptance Criteria:**
*   **Given** tôi đã hoàn thành nhiều buổi phỏng vấn ảo, **When** tôi truy cập trang lịch sử phỏng vấn, **Then** tôi thấy danh sách các buổi phỏng vấn với thông tin tóm tắt (tên vị trí, ngày, điểm tổng thể). (Covers FR17)
*   **Given** tôi nhấp vào một mục trong danh sách lịch sử, **When** tôi muốn xem chi tiết, **Then** hệ thống điều hướng tôi đến báo cáo đánh giá chi tiết của buổi phỏng vấn đó.
*   **And** danh sách lịch sử được phân trang nếu có nhiều buổi phỏng vấn.

**Implementation Details:**
- **Backend:** Standard CRUD endpoints for interview sessions
- **API Endpoints:**
  - `GET /api/v1/interviews` - List all sessions for current user
  - `GET /api/v1/interviews/{id}` - Get session details
  - `GET /api/v1/interviews/{id}/transcript` - Get full conversation transcript
  - `GET /api/v1/interviews/{id}/evaluation` - Get evaluation report
- **Database:** Query `interview_sessions` table with related data
- **Frontend:** 
  - List view with cards showing session summary
  - Detail view showing full transcript with per-turn scores
  - Evaluation report view with charts and recommendations

### Epic 4: Khám phá và Quản lý Ứng viên bằng AI (AI-Powered Candidate Discovery & Management)
**Mục tiêu:** Trao quyền cho nhà tuyển dụng đăng tin, tìm kiếm, xếp hạng và quản lý các ứng viên tiềm năng một cách hiệu quả.
**FRs bao gồm:** FR18, FR19, FR20, FR21, FR22, FR23, FR24

### Story 4.1: Tải lên & Quản lý Mô tả Công việc (Upload & Manage Job Descriptions)
As a nhà tuyển dụng,
I want để tải lên và quản lý các mô tả công việc (JD) của mình,
So that tôi có thể dễ dàng tìm kiếm và đối sánh ứng viên phù hợp.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập với vai trò nhà tuyển dụng, **When** tôi tải lên một JD (text hoặc tệp), **Then** JD đó được lưu trữ và hệ thống bắt đầu phân tích để trích xuất các yêu cầu. (Covers FR18, FR19, AR6)
*   **Given** tôi có các JD đã tải lên, **When** tôi truy cập trang quản lý JD, **Then** tôi thấy danh sách các JD với tiêu đề, trạng thái phân tích và tùy chọn xem/sửa/xóa. (Covers FR20)
*   **Given** JD đã được phân tích, **When** tôi xem chi tiết JD, **Then** tôi thấy các yêu cầu đã trích xuất (kỹ năng, kinh nghiệm tối thiểu).

### Story 4.2: Tìm kiếm & Xếp hạng Ứng viên (Candidate Search & Ranking)
As a nhà tuyển dụng,
I want để tìm kiếm ứng viên bằng truy vấn ngôn ngữ tự nhiên hoặc xếp hạng ứng viên theo một JD,
So that tôi có thể nhanh chóng tìm thấy những ứng viên phù hợp nhất.
**Acceptance Criteria:**
*   **Given** tôi có một JD đã được phân tích, **When** tôi yêu cầu xem các ứng viên phù hợp, **Then** hệ thống hiển thị danh sách các ứng viên đã được xếp hạng theo mức độ phù hợp với JD đó. (Covers FR21, AR7)
*   **Given** tôi muốn tìm kiếm ứng viên mà không cần JD cụ thể, **When** tôi nhập một truy vấn ngôn ngữ tự nhiên (ví dụ: "lập trình viên Python có kinh nghiệm về AWS"), **Then** hệ thống trả về danh sách ứng viên phù hợp với truy vấn. (Covers FR22, AR8)
*   **Given** một ứng viên có CV là riêng tư, **When** tôi tìm kiếm hoặc xếp hạng, **Then** tôi có thể thấy điểm phù hợp và tóm tắt, nhưng không thể xem chi tiết CV. (Covers NFR2.2)

### Story 4.3: Quản lý Bộ sưu tập Ứng viên (Candidate Collections Management)
As a nhà tuyển dụng,
I want để tạo và quản lý các "bộ sưu tập" ứng viên,
So that tôi có thể sắp xếp và lưu trữ các ứng viên tiềm năng cho các vị trí hiện tại hoặc tương lai.
**Acceptance Criteria:**
*   **Given** tôi đã tìm thấy các ứng viên phù hợp, **When** tôi thêm ứng viên vào một bộ sưu tập, **Then** ứng viên đó được lưu vào bộ sưu tập đã chọn. (Covers FR23)
*   **Given** tôi có các bộ sưu tập, **When** tôi truy cập trang bộ sưu tập, **Then** tôi thấy danh sách các bộ sưu tập của mình và các ứng viên trong đó.
*   **Given** tôi xóa một ứng viên khỏi bộ sưu tập, **When** tôi xác nhận, **Then** ứng viên đó bị xóa khỏi bộ sưu tập.

### Story 4.4: Xem Hồ sơ Ứng viên cho Nhà tuyển dụng (Recruiter's Candidate Profile View)
As a nhà tuyển dụng,
I want để xem phân tích CV công khai và kết quả phỏng vấn AI của một ứng viên,
So that tôi có thể đưa ra quyết định tuyển dụng sáng suốt.
**Acceptance Criteria:**
*   **Given** tôi đã tìm thấy một ứng viên có CV công khai, **When** tôi truy cập hồ sơ của ứng viên đó, **Then** tôi có thể xem phân tích CV chi tiết và báo cáo phỏng vấn AI (nếu có). (Covers FR24)
*   **Given** ứng viên đó đã đặt CV là riêng tư, **When** tôi cố gắng xem chi tiết hồ sơ, **Then** hệ thống hiển thị thông báo "CV này là riêng tư" và không hiển thị thông tin chi tiết. (Covers NFR2.2)

### Epic 5: Giao tiếp Thời gian thực (Real-time Communication) ✅ COMPLETED
**Mục tiêu:** Xây dựng một kênh giao tiếp tức thời giữa nhà tuyển dụng và ứng viên để tăng tốc quá trình tuyển dụng.
**FRs bao gồm:** FR25, FR26, FR27
**Completion Date:** January 7, 2026
**Status:** All 3 stories completed and tested. 11 issues fixed, 1 enhancement added.
**Tech Stack:** FastAPI backend, Socket.io server (port 3001), Next.js frontend with real-time Socket.io client.

### Story 5.1: Bắt đầu Cuộc Trò chuyện (Initiate Conversation) ✅ COMPLETED
As a nhà tuyển dụng,
I want để bắt đầu một cuộc trò chuyện với một ứng viên,
So that tôi có thể giao tiếp trực tiếp để sàng lọc hoặc sắp xếp phỏng vấn.
**Acceptance Criteria:**
*   ✅ **Given** tôi đã tìm thấy một ứng viên phù hợp, **When** tôi nhấp vào nút "Bắt đầu Trò chuyện", **Then** một giao diện trò chuyện mới mở ra và tôi có thể gửi tin nhắn đầu tiên. (Covers FR25)
*   ✅ **Given** đã có một cuộc trò chuyện với ứng viên đó, **When** tôi cố gắng bắt đầu cuộc trò chuyện mới, **Then** hệ thống đưa tôi đến cuộc trò chuyện hiện có.
*   ✅ **Given** tôi gửi tin nhắn, **When** tin nhắn được gửi, **Then** tin nhắn của tôi xuất hiện trong giao diện trò chuyện và được gửi đến ứng viên. (Covers NFR1.2)
**Implementation:** Enhanced với smart conversation detection - kiểm tra existing conversation trước khi mở modal.

### Story 5.2: Gửi và Nhận Tin nhắn (Send and Receive Messages) ✅ COMPLETED
As a người dùng (nhà tuyển dụng hoặc ứng viên),
I want để gửi và nhận tin nhắn thời gian thực trong giao diện trò chuyện,
So that tôi có thể trao đổi thông tin liên tục và hiệu quả.
**Acceptance Criteria:**
*   ✅ **Given** tôi đang ở trong giao diện trò chuyện, **When** tôi nhập tin nhắn và gửi, **Then** tin nhắn của tôi xuất hiện ngay lập tức trong cuộc trò chuyện và người đối thoại nhận được tin nhắn. (Covers FR26, NFR1.2, UXR3)
*   ✅ **Given** tôi nhận được tin nhắn mới, **When** tin nhắn đến, **Then** tin nhắn đó hiển thị ngay lập tức trong giao diện trò chuyện.
*   ✅ **And** tất cả tin nhắn được lưu trữ an toàn và có thể truy cập lại sau này. (Covers NFR2.1)
**Implementation:** Real-time via Socket.io. Own messages: blue/right-aligned. Received: gray/left-aligned with sender name.

### Story 5.3: Danh sách & Lịch sử Cuộc Trò chuyện (Conversation List & History) ✅ COMPLETED
As a người dùng,
I want để xem danh sách tất cả các cuộc trò chuyện của mình và truy cập lịch sử tin nhắn,
So that tôi có thể dễ dàng quản lý các trao đổi và theo dõi thông tin.
**Acceptance Criteria:**
*   ✅ **Given** tôi đã đăng nhập, **When** tôi truy cập trang tin nhắn, **Then** tôi thấy danh sách các cuộc trò chuyện của mình, sắp xếp theo tin nhắn gần nhất. (Covers FR27)
*   ✅ **Given** một cuộc trò chuyện có tin nhắn chưa đọc, **When** tôi xem danh sách, **Then** cuộc trò chuyện đó được đánh dấu là có tin nhắn mới.
*   ✅ **Given** tôi chọn một cuộc trò chuyện từ danh sách, **When** tôi nhấp vào, **Then** hệ thống đưa tôi đến giao diện trò chuyện với lịch sử tin nhắn đầy đủ.
**Implementation:** Route `/messages` displays conversation list với participant names, avatars, và last message preview.

### Epic 6: Giám sát và Quản trị Hệ thống (Admin Oversight & Monitoring)
**Mục tiêu:** Cung cấp cho quản trị viên các công cụ cần thiết để giám sát sức khỏe hệ thống và quản lý người dùng, nội dung.
**FRs bao gồm:** FR28, FR29, FR30, FR31

### Story 6.1: Dashboard Giám sát Hệ thống (System Monitoring Dashboard)
As an quản trị viên,
I want để xem một dashboard giám sát với các chỉ số sức khỏe hệ thống (GPU, RAM, độ trễ),
So that tôi có thể nhanh chóng đánh giá trạng thái hoạt động của nền tảng.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập với vai trò quản trị viên, **When** tôi truy cập dashboard quản trị, **Then** tôi thấy các biểu đồ và chỉ số về sử dụng CPU/RAM, GPU (nếu có) và độ trễ phản hồi của AI. (Covers FR28, UXR7)
*   **Given** các chỉ số hệ thống thay đổi, **When** tôi xem dashboard, **Then** các biểu đồ được cập nhật theo thời gian thực. (Covers NFR1.1)
*   **Given** một chỉ số vượt ngưỡng an toàn, **When** tôi xem dashboard, **Then** chỉ số đó được đánh dấu cảnh báo.
*   **And** chỉ quản trị viên mới có thể truy cập dashboard này. (Covers NFR2.2)

### Story 6.2: Xem Log Hệ thống (View System Logs)
As an quản trị viên,
I want để xem log hệ thống,
So that tôi có thể dễ dàng gỡ lỗi và theo dõi các sự kiện quan trọng.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập với vai trò quản trị viên, **When** tôi truy cập công cụ xem log, **Then** tôi thấy danh sách các log hệ thống với thông tin chi tiết (thời gian, cấp độ, thông báo). (Covers FR29)
*   **Given** có nhiều log, **When** tôi xem danh sách log, **Then** danh sách được phân trang và tôi có thể lọc theo cấp độ (INFO, WARNING, ERROR) hoặc tìm kiếm theo từ khóa.
*   **And** chỉ quản trị viên mới có thể xem log hệ thống. (Covers NFR2.2)

### Story 6.3: Quản lý Người dùng (User Management)
As an quản trị viên,
I want để xem và quản lý danh sách người dùng,
So that tôi có thể kiểm soát quyền truy cập và duy trì môi trường người dùng lành mạnh.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập với vai trò quản trị viên, **When** tôi truy cập trang quản lý người dùng, **Then** tôi thấy danh sách tất cả người dùng với thông tin cơ bản (email, vai trò, trạng thái hoạt động). (Covers FR30)
*   **Given** một người dùng vi phạm chính sách, **When** tôi chọn người dùng đó và thực hiện hành động khóa/mở khóa tài khoản, **Then** trạng thái tài khoản của họ được cập nhật ngay lập tức. (Covers AR9)
*   **Given** tôi muốn tìm kiếm người dùng cụ thể, **When** tôi sử dụng bộ lọc tìm kiếm, **Then** danh sách người dùng được cập nhật theo tiêu chí tìm kiếm.
*   **And** chỉ quản trị viên mới có thể quản lý người dùng. (Covers NFR2.2)

### Story 6.4: Quản lý Nội dung (Content Management)
As an quản trị viên,
I want để quản lý và kiểm duyệt nội dung (JD, CV công khai),
So that tôi có thể đảm bảo nền tảng tuân thủ các chính sách và an toàn.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập với vai trò quản trị viên, **When** tôi truy cập trang quản lý nội dung, **Then** tôi thấy danh sách các JD và CV công khai. (Covers FR31)
*   **Given** tôi phát hiện nội dung không phù hợp, **When** tôi chọn nội dung đó và thực hiện hành động ẩn/hiện, **Then** trạng thái hiển thị của nội dung được cập nhật và thay đổi trên nền tảng.
*   **And** chỉ quản trị viên mới có thể quản lý nội dung. (Covers NFR2.2)

### Epic 1: Nền tảng Xác thực và Quản lý Người dùng (User Authentication & Profile Foundation)
**Mục tiêu:** Cung cấp một hệ thống đăng ký, đăng nhập và quản lý tài khoản an toàn, tạo nền tảng cho tất cả các tính năng khác.
**FRs bao gồm:** FR1, FR2, FR3, FR4, FR5

### Story 1.1: Đăng ký Tài khoản Người dùng (User Registration)
As a người dùng mới,
I want để đăng ký tài khoản với vai trò 'Người tìm việc' hoặc 'Nhà tuyển dụng',
So that tôi có thể truy cập các tính năng của nền tảng.
**Acceptance Criteria:**
*   **Given** tôi chưa có tài khoản, **When** tôi cung cấp email hợp lệ, mật khẩu mạnh và chọn vai trò ('Người tìm việc' hoặc 'Nhà tuyển dụng'), **Then** tài khoản mới của tôi được tạo và tôi nhận được thông báo đăng ký thành công. (Covers FR1)
*   **Given** tôi cung cấp một email đã tồn tại, **When** tôi cố gắng đăng ký, **Then** hệ thống hiển thị thông báo lỗi 'Email đã được sử dụng'.
*   **Given** tôi cung cấp mật khẩu yếu hoặc không hợp lệ, **When** tôi cố gắng đăng ký, **Then** hệ thống hiển thị thông báo lỗi về yêu cầu mật khẩu.
*   **Given** tôi chọn vai trò không hợp lệ, **When** tôi cố gắng đăng ký, **Then** hệ thống hiển thị thông báo lỗi.
*   **And** mật khẩu được băm và lưu trữ an toàn. (Covers NFR2.4)
*   **And** vai trò người dùng được lưu trữ trong cơ sở dữ liệu. (Covers AR14)

### Story 1.2: Đăng nhập Người dùng (User Login)
As a người dùng đã đăng ký,
I want để đăng nhập bằng email và mật khẩu của mình,
So that tôi có thể truy cập các tính năng cá nhân hóa của nền tảng.
**Acceptance Criteria:**
*   **Given** tôi đã đăng ký tài khoản, **When** tôi nhập email và mật khẩu hợp lệ, **Then** hệ thống đăng nhập tôi thành công và cấp một cookie xác thực an toàn (HttpOnly). (Covers FR2, AR2)
*   **Given** tôi nhập email không tồn tại hoặc mật khẩu không đúng, **When** tôi cố gắng đăng nhập, **Then** hệ thống hiển thị thông báo lỗi 'Thông tin đăng nhập không hợp lệ'.
*   **Given** tôi là người dùng đã bị cấm, **When** tôi cố gắng đăng nhập, **Then** hệ thống hiển thị thông báo lỗi 'Tài khoản của bạn đã bị khóa'. (Covers AR14)
*   **And** cookie xác thực được lưu trữ dưới dạng HttpOnly để tăng cường bảo mật. (Covers NFR2.1)

### Story 1.3: Xem và Quản lý Hồ sơ Người dùng (View & Manage User Profile)
As a người dùng đã đăng nhập,
I want để xem thông tin cá nhân của mình và thay đổi mật khẩu,
So that tôi có thể cập nhật thông tin và duy trì bảo mật tài khoản.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập, **When** tôi truy cập trang hồ sơ, **Then** tôi có thể thấy email và ngày tham gia của mình. (Covers FR3)
*   **Given** tôi muốn thay đổi mật khẩu, **When** tôi cung cấp mật khẩu hiện tại chính xác và mật khẩu mới hợp lệ, **Then** mật khẩu của tôi được cập nhật thành công và tôi nhận được thông báo xác nhận. (Covers FR4)
*   **Given** tôi cung cấp mật khẩu hiện tại không đúng, **When** tôi cố gắng thay đổi mật khẩu, **Then** hệ thống hiển thị thông báo lỗi.
*   **Given** tôi không cung cấp mật khẩu mới mạnh hoặc hợp lệ, **When** tôi cố gắng thay đổi mật khẩu, **Thì** hệ thống hiển thị thông báo lỗi.
*   **And** các thay đổi mật khẩu được mã hóa an toàn. (Covers NFR2.4)

### Story 1.4: Xóa Tài khoản Người dùng (User Account Deletion)
As a người dùng đã đăng nhập,
I want để xóa tài khoản của mình và tất cả dữ liệu liên quan,
So that tôi có thể kiểm soát hoàn toàn thông tin cá nhân và quyền riêng tư của mình.
**Acceptance Criteria:**
*   **Given** tôi đã đăng nhập, **When** tôi yêu cầu xóa tài khoản và xác nhận thao tác này, **Thì** tài khoản của tôi và tất cả dữ liệu liên quan (CV, JD, v.v.) bị xóa vĩnh viễn khỏi nền tảng. (Covers FR5, NFR2.1)
*   **Given** tôi không xác nhận thao tác xóa tài khoản, **When** tôi yêu cầu xóa, **Thì** tài khoản của tôi không bị xóa.
*   **And** hệ thống hiển thị thông báo xác nhận xóa tài khoản thành công.
*   **And** các dữ liệu liên quan được xóa một cách toàn vẹn.
