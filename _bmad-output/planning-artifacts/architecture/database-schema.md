# Database Schema

## **Revised `Database Schema` (Updated with Vector Dimension 768)**

```sql
-- Assumes the 'pgvector' extension is installed: CREATE EXTENSION IF NOT EXISTS vector;

-- Existing 'users' table (with role-based access control)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Role-based access control (Story 4.1)
    role VARCHAR(20) NOT NULL DEFAULT 'job_seeker' 
        CHECK (role IN ('job_seeker', 'recruiter', 'admin')),
    
    -- Ban management (Story 4.5)
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    banned_at TIMESTAMP WITHOUT TIME ZONE,
    banned_reason TEXT,
    
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users (is_banned) WHERE is_banned = TRUE;

--------------------------------------------------------------------------------

-- New 'cvs' table
CREATE TABLE IF NOT EXISTS cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_content JSONB,
    summary TEXT,
    quality_score INTEGER,
    ats_compatibility_feedback TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Indexed fields for filtering
    extracted_skills TEXT[],
    total_experience_years INTEGER,

    -- NEW: Vector embedding for semantic search, dimension 768 as specified
    embedding VECTOR(768),

    -- Foreign key constraint with ON DELETE CASCADE
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cvs_user_id ON cvs (user_id);
CREATE INDEX IF NOT EXISTS idx_cvs_extracted_skills ON cvs USING GIN (extracted_skills);
CREATE INDEX IF NOT EXISTS idx_cvs_total_experience_years ON cvs (total_experience_years);
-- NEW: Index for vector similarity search (e.g., IVFFlat)
CREATE INDEX IF NOT EXISTS idx_cvs_embedding ON cvs USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

--------------------------------------------------------------------------------

-- New 'job_descriptions' table
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Structured fields for filtering
    required_skills TEXT[],
    min_experience_years INTEGER,
    location_type VARCHAR(50) NOT NULL CHECK (location_type IN ('remote', 'hybrid', 'on-site')),
    salary_min INTEGER,
    salary_max INTEGER,

    -- NEW: Vector embedding for semantic search, dimension 768 as specified
    embedding VECTOR(768),

    -- Foreign key constraint with ON DELETE CASCADE
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_required_skills ON job_descriptions USING GIN (required_skills);
-- ... other indexes from before ...
-- NEW: Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_job_descriptions_embedding ON job_descriptions USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

---