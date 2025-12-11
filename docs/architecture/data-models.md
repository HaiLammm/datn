# Data Models

## **Updated `CV` Model (Hybrid Approach)**

**Purpose:** To store uploaded CVs, their full parsed content, and key indexed fields for efficient searching.

**Key Attributes:**
- `id`: UUID
- `user_id`: UUID
- `filename`: String
- `file_path`: String
- `uploaded_at`: DateTime
- `parsed_content`: **JSONB** - _(Contains the full, raw AI extraction for flexibility)._
- `summary`: Text
- `quality_score`: Integer
- `ats_compatibility_feedback`: Text
- `is_active`: Boolean
- `extracted_skills`: **Array of Text** - _(NEW - Indexed for fast skill-based searches)._
- `total_experience_years`: **Integer** - _(NEW - Indexed for filtering by experience level)._

### TypeScript Interface
```typescript
interface CV {
  id: string;
  userId: string;
  filename: string;
  filePath: string;
  uploadedAt: string;
  parsedContent: Record<string, any>;
  summary: string;
  qualityScore: number;
  atsCompatibilityFeedback: string;
  isActive: boolean;
  extractedSkills: string[]; // NEW
  totalExperienceYears: number; // NEW
}
```

---

## **Updated `JobDescription` Model (Structured Approach)**

**Purpose:** To store job descriptions with both full-text for semantic search and structured fields for precise filtering.

**Key Attributes:**
- `id`: UUID
- `user_id`: UUID
- `title`: String
- `description`: Text - _(Full original text for semantic matching)._
- `uploaded_at`: DateTime
- `is_active`: Boolean
- `required_skills`: **Array of Text** - _(NEW - For skill-based matching and filtering)._
- `min_experience_years`: **Integer** - _(NEW - For filtering by minimum experience)._
- `location_type`: **String** (`'remote' | 'hybrid' | 'on-site'`) - _(NEW - For location-based filtering)._
- `salary_min`: **Integer** - _(NEW - For salary range filtering)._
- `salary_max`: **Integer** - _(NEW - For salary range filtering)._

### TypeScript Interface
```typescript
type LocationType = 'remote' | 'hybrid' | 'on-site';

interface JobDescription {
  id: string;
  userId: string;
  title: string;
  description: string;
  uploadedAt: string;
  isActive: boolean;
  requiredSkills: string[]; // NEW
  minExperienceYears: number; // NEW
  locationType: LocationType; // NEW
  salaryMin?: number; // NEW - Optional
  salaryMax?: number; // NEW - Optional
}
```

---