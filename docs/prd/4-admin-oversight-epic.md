# Epic 4: Admin Oversight & Monitoring

## 4.1. Goals and Background Context

### 4.1.1. Goals

- Cung cap dashboard giam sat real-time cho AI infrastructure (GPU/RAM, latency)
- Cho phep Admin truy cap system logs lien quan den AI pipeline
- Trien khai cong cu quan ly user co ban (view, ban/suspend)
- Hien thi cac metrics quan trong cua he thong (DAU, CVs parsed, etc.)
- Dam bao Admin co visibility vao health cua platform

### 4.1.2. Background Context

He thong hien tai thieu cong cu monitoring va quan ly cho Admin:
- Khong co cach theo doi AI service performance
- Khong co giao dien quan ly users
- System logs chi accessible qua terminal

**PRD Requirements Addressed:**
| Requirement | Description |
|-------------|-------------|
| **FR9** | Display real-time server resource utilization (GPU/RAM) |
| **FR10** | Monitor and display AI inference latency |
| **FR11** | Provide access to system logs related to AI pipeline |

**From Project Brief (Admin Oversight):**
- User monitoring and account management
- Ban/suspend capabilities
- Content moderation (flagged CVs/JDs)
- Real-time resource monitoring
- System logs and audit trails

### 4.1.3. Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-17 | 0.1.0 | Initial PRD draft for Admin Oversight | John (PM) |

---

## 4.2. Requirements

### 4.2.1. Functional Requirements

| ID | Requirement |
|----|-------------|
| **FR-AO1** | He thong phai hien thi real-time CPU/RAM usage cua server |
| **FR-AO2** | He thong phai hien thi GPU usage neu co GPU available |
| **FR-AO3** | He thong phai track va hien thi AI inference latency (avg, p95, p99) |
| **FR-AO4** | He thong phai hien thi Ollama service status (up/down, model loaded) |
| **FR-AO5** | He thong phai cho phep Admin xem system logs (last N entries) |
| **FR-AO6** | He thong phai filter logs theo level (INFO, WARNING, ERROR) |
| **FR-AO7** | He thong phai hien thi danh sach tat ca users voi basic info |
| **FR-AO8** | He thong phai cho phep Admin ban/suspend user accounts |
| **FR-AO9** | He thong phai hien thi key metrics: DAU, total users, CVs analyzed |
| **FR-AO10** | He thong phai restrict Admin features chi cho users co admin role |

### 4.2.2. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| **NFR-AO1** | Resource monitoring phai update moi 5-10 seconds |
| **NFR-AO2** | Admin dashboard phai load trong thoi gian chap nhan duoc |
| **NFR-AO3** | Log viewer phai handle large log files efficiently (pagination) |
| **NFR-AO4** | Admin actions phai duoc audit logged |

### 4.2.3. Compatibility Requirements

| ID | Requirement |
|----|-------------|
| **CR-AO1** | Monitoring endpoints phai khong anh huong toi performance cua main API |
| **CR-AO2** | Admin role phai integrate voi existing auth system |
| **CR-AO3** | UI phai consistent voi existing design system |

---

## 4.3. User Interface Enhancement Goals

### 4.3.1. New Screens Required

| Screen | Description |
|--------|-------------|
| **Admin Dashboard** | Overview voi key metrics va quick status |
| **System Monitoring** | Real-time resource utilization charts |
| **AI Service Status** | Ollama health, model info, latency stats |
| **Log Viewer** | Searchable, filterable log display |
| **User Management** | User list voi actions |

### 4.3.2. UI Mockup

```
+-------------------------------------------------------------+
|                     Admin Dashboard                          |
+-------------------------------------------------------------+
|                                                             |
|  +-------------+ +-------------+ +-------------+ +---------+|
|  | Total Users | | CVs Today   | | Active Now  | |AI Status||
|  |    1,234    | |     56      | |     23      | |  OK     ||
|  +-------------+ +-------------+ +-------------+ +---------+|
|                                                             |
|  +-------------------------------------------------------------+
|  |  System Resources                                       |
|  |  CPU:  ================....  65%                       |
|  |  RAM:  =============.......  52%  (8.3 / 16 GB)        |
|  |  GPU:  ==========..........  42%  (2.5 / 6 GB VRAM)    |
|  +-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  |  AI Inference Latency                                   |
|  |  Average: 2.3s  |  P95: 4.5s  |  P99: 8.2s             |
|  |  Last 100 requests: ================                   |
|  +-------------------------------------------------------------+
|                                                             |
|  +-------------------------------------------------------------+
|  |  Recent Logs                               [View All ->] |
|  |  12:34:55 [INFO]  CV analysis completed for user #123   |
|  |  12:34:52 [WARN]  Ollama response slow (3.5s)          |
|  |  12:34:48 [INFO]  New user registered: test@example.com |
|  +-------------------------------------------------------------+
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                     User Management                          |
+-------------------------------------------------------------+
|  Search: [________________________]  Filter: [All v]        |
|                                                             |
|  +-------------------------------------------------------------+
|  | Email             | Status  | CVs | Created    | Action |
|  +-------------------+---------+-----+------------+--------+
|  | user1@example.com | Active  |  5  | 2025-12-01 | [Ban]  |
|  | user2@example.com | Active  |  3  | 2025-12-05 | [Ban]  |
|  | spam@test.com     | Banned  |  0  | 2025-12-10 |[Unban] |
|  +-------------------------------------------------------------+
|                                                             |
|  Showing 1-10 of 1,234 users    [<- Prev] [1] [2] [3] [Next ->]|
+-------------------------------------------------------------+
```

---

## 4.4. Technical Assumptions

### 4.4.1. Database Schema Updates

```sql
-- Add admin role to users table
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' 
    CHECK (role IN ('user', 'admin'));

-- Add is_banned column
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN banned_at TIMESTAMP;
ALTER TABLE users ADD COLUMN banned_reason TEXT;

-- AI metrics tracking table (optional, for historical data)
CREATE TABLE IF NOT EXISTS ai_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(50) NOT NULL,  -- 'inference_latency', 'cpu_usage', etc.
    value FLOAT NOT NULL,
    metadata JSONB
);

-- Audit log table
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id UUID,
    details JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4.4.2. API Endpoints

```yaml
# Admin endpoints (all require admin role)
GET    /api/v1/admin/metrics/system     # CPU, RAM, GPU usage
GET    /api/v1/admin/metrics/ai         # AI inference stats
GET    /api/v1/admin/metrics/overview   # Key platform metrics
GET    /api/v1/admin/logs               # System logs (paginated)
GET    /api/v1/admin/users              # List users (paginated)
GET    /api/v1/admin/users/{user_id}    # User details
POST   /api/v1/admin/users/{user_id}/ban    # Ban user
POST   /api/v1/admin/users/{user_id}/unban  # Unban user
GET    /api/v1/admin/ollama/status      # Ollama service status
```

### 4.4.3. New Files Structure

```
backend/app/modules/admin/
+-- __init__.py
+-- models.py          # AdminAuditLog model
+-- schemas.py         # Admin-related schemas
+-- service.py         # Admin operations
+-- router.py          # Admin API endpoints
+-- metrics_collector.py  # System metrics collection
+-- dependencies.py    # Admin role verification

frontend/app/admin/
+-- page.tsx           # Admin dashboard
+-- layout.tsx         # Admin layout with sidebar
+-- monitoring/
|   +-- page.tsx       # System monitoring
+-- logs/
|   +-- page.tsx       # Log viewer
+-- users/
    +-- page.tsx       # User management

frontend/features/admin/
+-- components/
|   +-- MetricsCard.tsx
|   +-- ResourceChart.tsx
|   +-- LatencyChart.tsx
|   +-- LogViewer.tsx
|   +-- UserTable.tsx
|   +-- AdminSidebar.tsx
+-- hooks/
|   +-- useMetrics.ts  # Polling hook for metrics
+-- actions.ts
```

---

## 4.5. User Stories

### Story 4.1: Admin Role & Authorization

**As a** developer,
**I want** admin role system implemented,
**So that** admin features are protected.

#### Acceptance Criteria

1. Them `role` column vao users table (values: 'user', 'admin')
2. Tao migration voi default role = 'user'
3. Tao `require_admin` dependency cho FastAPI
4. Admin endpoints return 403 cho non-admin users
5. Seed mot admin user cho testing
6. Frontend hien thi Admin link chi cho admin users

---

### Story 4.2: System Resource Monitoring API

**As an** Admin,
**I want** to view real-time system resources,
**So that** I can monitor server health.

#### Acceptance Criteria

1. Tao `/api/v1/admin/metrics/system` endpoint
2. Return CPU usage percentage
3. Return RAM usage (used, total, percentage)
4. Return GPU usage neu available (nvidia-smi)
5. Return disk usage
6. Handle errors gracefully (GPU not available, etc.)
7. Response time < 500ms

---

### Story 4.3: AI Service Metrics API

**As an** Admin,
**I want** to monitor AI inference performance,
**So that** I can identify bottlenecks.

#### Acceptance Criteria

1. Track AI inference latency trong AI service
2. Tao `/api/v1/admin/metrics/ai` endpoint
3. Return average latency (last N requests)
4. Return P95, P99 latency
5. Return success/failure counts
6. Return Ollama model info (name, size)
7. Tao `/api/v1/admin/ollama/status` cho health check

---

### Story 4.4: System Logs API

**As an** Admin,
**I want** to view system logs,
**So that** I can debug issues.

#### Acceptance Criteria

1. Configure Python logging to write to file
2. Tao `/api/v1/admin/logs` endpoint
3. Support pagination (limit, offset)
4. Support filtering by log level
5. Support searching by keyword
6. Return log entries voi timestamp, level, message
7. Handle large log files efficiently

---

### Story 4.5: User Management API

**As an** Admin,
**I want** to manage user accounts,
**So that** I can handle policy violations.

#### Acceptance Criteria

1. Them `is_banned`, `banned_at`, `banned_reason` columns
2. Tao `/api/v1/admin/users` endpoint (list with pagination)
3. Tao `/api/v1/admin/users/{id}/ban` endpoint
4. Tao `/api/v1/admin/users/{id}/unban` endpoint
5. Banned users cannot login (return appropriate error)
6. Log all ban/unban actions to audit log
7. Return user stats (CV count, last active)

---

### Story 4.6: Admin Dashboard Frontend

**As an** Admin,
**I want** a dashboard to see platform overview,
**So that** I can quickly assess system status.

#### Acceptance Criteria

1. Tao admin layout voi sidebar navigation
2. Dashboard hien thi key metrics cards
3. Resource usage charts voi auto-refresh
4. AI latency visualization
5. Recent logs preview
6. Quick links to detailed views
7. Responsive design

---

### Story 4.7: User Management Frontend

**As an** Admin,
**I want** a UI to manage users,
**So that** I can take actions efficiently.

#### Acceptance Criteria

1. User table voi pagination
2. Search by email
3. Filter by status (active, banned)
4. Ban/unban buttons voi confirmation modal
5. View user details (CV count, activity)
6. Show ban history if applicable
7. Export user list (optional)

---

## 4.6. Implementation Priority

| Priority | Story | Rationale |
|----------|-------|-----------|
| **P0 - Must Have** | 4.1 Admin Role | Security foundation |
| **P0 - Must Have** | 4.2 System Metrics | Core monitoring |
| **P0 - Must Have** | 4.3 AI Metrics | Core monitoring |
| **P1 - Should Have** | 4.5 User Management API | User control |
| **P1 - Should Have** | 4.6 Admin Dashboard | User-facing |
| **P2 - Nice to Have** | 4.4 Logs API | Debugging |
| **P2 - Nice to Have** | 4.7 User Management UI | Full admin experience |

---

## 4.7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Metrics collection impacts performance | Medium | Low | Lightweight collection, caching |
| GPU metrics not available | Low | Medium | Graceful degradation |
| Log file grows too large | Medium | Medium | Log rotation, pagination |
| Admin role misuse | High | Low | Audit logging, 2FA (future) |

---

## 4.8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Metrics endpoint response time | <500ms | API monitoring |
| Dashboard load time | <2s | Manual testing |
| Admin can ban user | Works correctly | Manual testing |
| System status visible | Real-time updates | Manual testing |

---

## 4.9. Dependencies

| Story | Depends On |
|-------|------------|
| 4.2 System Metrics | 4.1 Admin Role |
| 4.3 AI Metrics | 4.1 Admin Role |
| 4.4 Logs API | 4.1 Admin Role |
| 4.5 User Management | 4.1 Admin Role |
| 4.6 Dashboard Frontend | 4.2, 4.3 |
| 4.7 User Management UI | 4.5 |
