# Story 9.2: Bộ lọc tìm kiếm nâng cao

## Status
ready-for-dev

## Story
**As a** Job Seeker (Người tìm việc),
**I want** sử dụng các bộ lọc như mức lương, loại hình công việc (full-time/part-time), kỹ năng yêu cầu và phúc lợi,
**So that** tôi có thể tinh chỉnh kết quả tìm kiếm theo nhu cầu cá nhân.

## Acceptance Criteria

### AC1: Salary Range Filter
**Given** I am on the job search page with existing results from Story 9.1,
**When** I set a salary range filter (e.g., min: 1000, max: 3000 USD),
**Then** the system filters job descriptions where:
- `salary_min >= my_min_salary` OR `salary_max <= my_max_salary`
- Only jobs with salary information are shown
**And** the filter persists when I navigate between pages.

### AC2: Job Type Filter
**Given** I am on the job search page,
**When** I select one or more job types (e.g., "Full-time", "Part-time", "Contract", "Internship"),
**Then** the system returns only jobs where `job_type` matches one of the selected types,
**And** I can select multiple job types simultaneously (OR logic).

### AC3: Required Skills Filter
**Given** I am on the job search page,
**When** I enter required skills (e.g., "Python, React, SQL") using autocomplete input,
**Then** the system:
- Shows autocomplete suggestions from existing job skills in the database
- Filters jobs where `required_skills` array contains ANY of the selected skills (OR logic)
- Displays matched skills as chips/tags that can be removed individually.

### AC4: Benefits Filter
**Given** I am on the job search page,
**When** I select one or more benefits (e.g., "Health Insurance", "Remote Work", "Flexible Hours"),
**Then** the system filters jobs where `benefits` array contains ALL selected benefits (AND logic),
**And** benefits options are loaded from a predefined list or database.

### AC5: Combined Filters with Basic Search
**Given** I have entered keyword/location from Story 9.1,
**When** I apply advanced filters (salary, job type, skills, benefits),
**Then** the system applies ALL filters together:
- Keyword + Location (from Story 9.1)
- Salary range filter
- Job type filter
- Skills filter (OR)
- Benefits filter (AND)
**And** displays the count of results matching all criteria.

### AC6: Filter UI - Expandable Panel
**Given** I am on the job search page,
**When** I view the page,
**Then** I see an "Advanced Filters" expandable panel with:
- Collapsed by default on mobile
- Expanded by default on desktop
- Clear visual separation from search results
- "Apply Filters" button
- "Clear All Filters" button

### AC7: Filter State Management
**Given** I have applied filters,
**When** I navigate between pages or refresh the browser,
**Then** my selected filters are preserved in the URL query parameters,
**And** filters are automatically reapplied when I return to the page.

### AC8: Filter Feedback
**Given** I have applied filters,
**When** I view the search results,
**Then** I see:
- Active filter tags above results (e.g., "Salary: 1000-3000", "Skills: Python, React")
- Each tag has a remove (X) button to clear that specific filter
- Total results count updated to reflect filtered results
- "Clear all filters" link if any filter is active.

## Tasks / Subtasks

### Backend Implementation

- [ ] **Task 1: Database Schema Enhancement (AC: 1-4)**
    - [ ] Add migration to enhance `job_descriptions` table:
        ```sql
        ALTER TABLE job_descriptions
        ADD COLUMN salary_min INTEGER,
        ADD COLUMN salary_max INTEGER,
        ADD COLUMN job_type VARCHAR(50) CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance')),
        ADD COLUMN required_skills TEXT[] DEFAULT '{}',
        ADD COLUMN benefits TEXT[] DEFAULT '{}';
        ```
    - [ ] Add indexes for filter performance:
        ```sql
        -- Index for salary range queries
        CREATE INDEX idx_job_descriptions_salary ON job_descriptions(salary_min, salary_max);
        
        -- Index for job_type filtering
        CREATE INDEX idx_job_descriptions_job_type ON job_descriptions(job_type);
        
        -- GIN index for array containment queries on skills
        CREATE INDEX idx_job_descriptions_skills ON job_descriptions USING gin(required_skills);
        
        -- GIN index for array containment queries on benefits
        CREATE INDEX idx_job_descriptions_benefits ON job_descriptions USING gin(benefits);
        ```
    - [ ] Update existing `JobDescription` model in `backend/app/modules/jobs/models.py`

- [ ] **Task 2: Pydantic Schemas Enhancement (AC: All)**
    - [ ] Extend `JobSearchRequest` schema:
        ```python
        class JobSearchRequest(BaseModel):
            # Story 9.1 fields
            keyword: Optional[str] = None
            location: Optional[str] = None
            
            # Story 9.2 advanced filters
            min_salary: Optional[int] = Field(None, ge=0)
            max_salary: Optional[int] = Field(None, ge=0)
            job_types: Optional[List[str]] = Field(None, max_items=5)
            required_skills: Optional[List[str]] = Field(None, max_items=20)
            benefits: Optional[List[str]] = Field(None, max_items=10)
            
            # Pagination
            page: int = Field(default=1, ge=1)
            limit: int = Field(default=10, ge=1, le=50)
            
            @validator('max_salary')
            def validate_salary_range(cls, v, values):
                if v and values.get('min_salary') and v < values['min_salary']:
                    raise ValueError('max_salary must be >= min_salary')
                return v
        ```
    - [ ] Extend `JobSearchResult` schema to include new fields:
        ```python
        class JobSearchResult(BaseModel):
            id: UUID
            title: str
            company_name: str
            location_type: str
            job_type: Optional[str]
            salary_min: Optional[int]
            salary_max: Optional[int]
            required_skills: List[str]
            benefits: List[str]
            posted_date: str
            description_snippet: str
        ```
    - [ ] Add `SkillSuggestion` schema for autocomplete:
        ```python
        class SkillSuggestion(BaseModel):
            skill: str
            count: int  # How many jobs require this skill
        ```

- [ ] **Task 3: Advanced Search Service Layer (AC: 1-5)**
    - [ ] Enhance `search_jobs()` function in `backend/app/modules/jobs/service.py`:
        ```python
        async def search_jobs(
            db: AsyncSession,
            keyword: Optional[str] = None,
            location: Optional[str] = None,
            min_salary: Optional[int] = None,
            max_salary: Optional[int] = None,
            job_types: Optional[List[str]] = None,
            required_skills: Optional[List[str]] = None,
            benefits: Optional[List[str]] = None,
            page: int = 1,
            limit: int = 10
        ) -> Tuple[List[JobDescription], int]:
            # Start with base query from Story 9.1
            query = select(JobDescription).where(JobDescription.is_active == True)
            
            # Story 9.1 filters (keyword + location)
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.where(
                    or_(
                        JobDescription.title.ilike(search_pattern),
                        JobDescription.description.ilike(search_pattern)
                    )
                )
            
            if location:
                location_normalized = location.lower().strip()
                if location_normalized in ['remote', 'hybrid', 'on-site']:
                    query = query.where(JobDescription.location_type == location_normalized)
            
            # Story 9.2 advanced filters
            if min_salary is not None or max_salary is not None:
                # Filter jobs where salary range overlaps with user's range
                if min_salary is not None and max_salary is not None:
                    query = query.where(
                        or_(
                            and_(
                                JobDescription.salary_min.isnot(None),
                                JobDescription.salary_min >= min_salary,
                                JobDescription.salary_max <= max_salary
                            ),
                            and_(
                                JobDescription.salary_max.isnot(None),
                                JobDescription.salary_max >= min_salary
                            )
                        )
                    )
                elif min_salary is not None:
                    query = query.where(
                        or_(
                            JobDescription.salary_min >= min_salary,
                            JobDescription.salary_max >= min_salary
                        )
                    )
                elif max_salary is not None:
                    query = query.where(
                        JobDescription.salary_max <= max_salary
                    )
            
            if job_types:
                # OR logic: match any of the selected job types
                query = query.where(JobDescription.job_type.in_(job_types))
            
            if required_skills:
                # OR logic: match jobs that have ANY of the required skills
                query = query.where(
                    JobDescription.required_skills.overlap(required_skills)
                )
            
            if benefits:
                # AND logic: match jobs that have ALL selected benefits
                for benefit in benefits:
                    query = query.where(
                        JobDescription.benefits.contains([benefit])
                    )
            
            # Count total before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await db.scalar(count_query)
            
            # Apply pagination and sorting
            query = query.order_by(JobDescription.uploaded_at.desc())
            query = query.offset((page - 1) * limit).limit(limit)
            
            # Eager load recruiter to avoid N+1
            query = query.options(selectinload(JobDescription.recruiter))
            
            result = await db.execute(query)
            jobs = result.scalars().all()
            
            return jobs, total_count
        ```
    - [ ] Add skill autocomplete service:
        ```python
        async def get_skill_suggestions(
            db: AsyncSession,
            query: str,
            limit: int = 10
        ) -> List[SkillSuggestion]:
            """Get autocomplete suggestions for skills based on existing job data."""
            stmt = select(
                func.unnest(JobDescription.required_skills).label('skill'),
                func.count().label('count')
            ).where(
                JobDescription.is_active == True
            ).where(
                func.unnest(JobDescription.required_skills).ilike(f"%{query}%")
            ).group_by('skill').order_by(func.count().desc()).limit(limit)
            
            result = await db.execute(stmt)
            return [
                SkillSuggestion(skill=row.skill, count=row.count)
                for row in result.all()
            ]
        ```

- [ ] **Task 4: API Endpoint Enhancement (AC: All)**
    - [ ] Update `GET /api/v1/jobs/search/basic` to accept new query parameters:
        ```python
        @router.get("/search/basic", response_model=schemas.JobSearchResponse)
        async def search_jobs_basic(
            # Story 9.1 parameters
            keyword: Optional[str] = Query(None, max_length=200),
            location: Optional[str] = Query(None, max_length=50),
            
            # Story 9.2 advanced filters
            min_salary: Optional[int] = Query(None, ge=0),
            max_salary: Optional[int] = Query(None, ge=0),
            job_types: Optional[List[str]] = Query(None, max_items=5),
            required_skills: Optional[List[str]] = Query(None, max_items=20),
            benefits: Optional[List[str]] = Query(None, max_items=10),
            
            # Pagination
            page: int = Query(1, ge=1),
            limit: int = Query(10, ge=1, le=50),
            
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(require_job_seeker)
        ):
            """
            Advanced job search with multiple filters.
            Builds on Story 9.1 basic search with salary, job type, skills, and benefits filters.
            """
            jobs, total_count = await service.search_jobs(
                db=db,
                keyword=keyword,
                location=location,
                min_salary=min_salary,
                max_salary=max_salary,
                job_types=job_types,
                required_skills=required_skills,
                benefits=benefits,
                page=page,
                limit=limit
            )
            
            # Transform to response format
            results = [
                schemas.JobSearchResult(
                    id=job.id,
                    title=job.title,
                    company_name=job.recruiter.email,
                    location_type=job.location_type,
                    job_type=job.job_type,
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    required_skills=job.required_skills or [],
                    benefits=job.benefits or [],
                    posted_date=format_relative_time(job.uploaded_at),
                    description_snippet=job.description[:150] + "..." if len(job.description) > 150 else job.description
                )
                for job in jobs
            ]
            
            total_pages = (total_count + limit - 1) // limit
            
            return schemas.JobSearchResponse(
                results=results,
                total_count=total_count,
                page=page,
                total_pages=total_pages
            )
        ```
    - [ ] Add skill autocomplete endpoint:
        ```python
        @router.get("/skills/autocomplete", response_model=List[schemas.SkillSuggestion])
        async def autocomplete_skills(
            q: str = Query(..., min_length=2, max_length=50),
            limit: int = Query(10, ge=1, le=20),
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(require_job_seeker)
        ):
            """Get skill autocomplete suggestions based on existing job data."""
            return await service.get_skill_suggestions(db, q, limit)
        ```

- [ ] **Task 5: Testing (AC: All)**
    - [ ] In `backend/tests/modules/jobs/test_search_service.py`:
        - [ ] `test_search_by_salary_range` - Verify salary filter works
        - [ ] `test_search_by_job_types` - Verify job type filter (OR logic)
        - [ ] `test_search_by_skills` - Verify skills filter (OR logic)
        - [ ] `test_search_by_benefits` - Verify benefits filter (AND logic)
        - [ ] `test_search_combined_all_filters` - Verify all filters together
        - [ ] `test_search_salary_overlap` - Verify salary range overlap logic
        - [ ] `test_skill_autocomplete` - Verify skill suggestions
    - [ ] In `backend/tests/modules/jobs/test_job_router.py`:
        - [ ] `test_advanced_search_endpoint` - Verify new parameters
        - [ ] `test_skill_autocomplete_endpoint` - Verify autocomplete endpoint
        - [ ] `test_advanced_search_validation` - Verify salary validation (max >= min)

### Frontend Implementation

- [ ] **Task 6: Enhanced Server Actions (AC: All)**
    - [ ] Update `searchJobsAction` in `frontend/features/jobs/actions.ts`:
        ```typescript
        'use server';
        
        import { cookies } from 'next/headers';
        import apiClient from '@/services/api-client';
        
        export interface AdvancedSearchFilters {
          keyword?: string;
          location?: string;
          minSalary?: number;
          maxSalary?: number;
          jobTypes?: string[];
          requiredSkills?: string[];
          benefits?: string[];
          page?: number;
        }
        
        export async function searchJobsAction(filters: AdvancedSearchFilters) {
          try {
            const cookieStore = await cookies();
            const token = cookieStore.get('access_token')?.value;
            
            if (!token) {
              return { error: 'Unauthorized' };
            }
            
            // Build query params, converting arrays to repeated params
            const params = new URLSearchParams();
            if (filters.keyword) params.append('keyword', filters.keyword);
            if (filters.location) params.append('location', filters.location);
            if (filters.minSalary) params.append('min_salary', filters.minSalary.toString());
            if (filters.maxSalary) params.append('max_salary', filters.maxSalary.toString());
            if (filters.jobTypes) {
              filters.jobTypes.forEach(type => params.append('job_types', type));
            }
            if (filters.requiredSkills) {
              filters.requiredSkills.forEach(skill => params.append('required_skills', skill));
            }
            if (filters.benefits) {
              filters.benefits.forEach(benefit => params.append('benefits', benefit));
            }
            params.append('page', (filters.page || 1).toString());
            params.append('limit', '10');
            
            const response = await apiClient.get(`/jobs/search/basic?${params.toString()}`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            
            return { data: response.data };
          } catch (error) {
            console.error('Search jobs error:', error);
            return { error: 'Failed to search jobs' };
          }
        }
        
        export async function getSkillSuggestionsAction(query: string) {
          try {
            const cookieStore = await cookies();
            const token = cookieStore.get('access_token')?.value;
            
            if (!token) return { error: 'Unauthorized' };
            
            const response = await apiClient.get('/jobs/skills/autocomplete', {
              params: { q: query, limit: 10 },
              headers: { Authorization: `Bearer ${token}` }
            });
            
            return { data: response.data };
          } catch (error) {
            return { error: 'Failed to fetch suggestions' };
          }
        }
        ```

- [ ] **Task 7: Advanced Filters Panel Component (AC: 6-8)**
    - [ ] Create `frontend/features/jobs/components/AdvancedFilters.tsx`:
        ```typescript
        'use client';
        
        import { useState } from 'react';
        import { Input } from '@/components/ui/input';
        import { Button } from '@/components/ui/button';
        import { Label } from '@/components/ui/label';
        import { Checkbox } from '@/components/ui/checkbox';
        import { Badge } from '@/components/ui/badge';
        import { ChevronDown, ChevronUp, X } from 'lucide-react';
        import { SkillAutocomplete } from './SkillAutocomplete';
        
        interface AdvancedFiltersProps {
          onApplyFilters: (filters: AdvancedSearchFilters) => void;
          onClearFilters: () => void;
        }
        
        export function AdvancedFilters({ onApplyFilters, onClearFilters }: AdvancedFiltersProps) {
          const [isExpanded, setIsExpanded] = useState(false);
          const [minSalary, setMinSalary] = useState('');
          const [maxSalary, setMaxSalary] = useState('');
          const [selectedJobTypes, setSelectedJobTypes] = useState<string[]>([]);
          const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
          const [selectedBenefits, setSelectedBenefits] = useState<string[]>([]);
          
          const jobTypeOptions = [
            { value: 'full-time', label: 'Full-time' },
            { value: 'part-time', label: 'Part-time' },
            { value: 'contract', label: 'Contract' },
            { value: 'internship', label: 'Internship' },
            { value: 'freelance', label: 'Freelance' },
          ];
          
          const benefitOptions = [
            'Health Insurance',
            'Remote Work',
            'Flexible Hours',
            'Paid Time Off',
            'Learning Budget',
            'Gym Membership',
          ];
          
          const handleApply = () => {
            onApplyFilters({
              minSalary: minSalary ? parseInt(minSalary) : undefined,
              maxSalary: maxSalary ? parseInt(maxSalary) : undefined,
              jobTypes: selectedJobTypes.length > 0 ? selectedJobTypes : undefined,
              requiredSkills: selectedSkills.length > 0 ? selectedSkills : undefined,
              benefits: selectedBenefits.length > 0 ? selectedBenefits : undefined,
            });
          };
          
          const handleClear = () => {
            setMinSalary('');
            setMaxSalary('');
            setSelectedJobTypes([]);
            setSelectedSkills([]);
            setSelectedBenefits([]);
            onClearFilters();
          };
          
          return (
            <div className="bg-white p-4 rounded-lg shadow mb-6">
              {/* Header */}
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                <h3 className="text-lg font-semibold">Bộ lọc nâng cao</h3>
                {isExpanded ? <ChevronUp /> : <ChevronDown />}
              </div>
              
              {/* Filters Content */}
              {isExpanded && (
                <div className="mt-4 space-y-6">
                  {/* Salary Range */}
                  <div>
                    <Label className="mb-2">Khoảng lương (USD)</Label>
                    <div className="flex gap-2 items-center">
                      <Input
                        type="number"
                        placeholder="Min"
                        value={minSalary}
                        onChange={(e) => setMinSalary(e.target.value)}
                      />
                      <span>-</span>
                      <Input
                        type="number"
                        placeholder="Max"
                        value={maxSalary}
                        onChange={(e) => setMaxSalary(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  {/* Job Types */}
                  <div>
                    <Label className="mb-2">Loại hình công việc</Label>
                    <div className="space-y-2">
                      {jobTypeOptions.map((option) => (
                        <div key={option.value} className="flex items-center gap-2">
                          <Checkbox
                            checked={selectedJobTypes.includes(option.value)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedJobTypes([...selectedJobTypes, option.value]);
                              } else {
                                setSelectedJobTypes(selectedJobTypes.filter(t => t !== option.value));
                              }
                            }}
                          />
                          <label>{option.label}</label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Required Skills */}
                  <div>
                    <Label className="mb-2">Kỹ năng yêu cầu</Label>
                    <SkillAutocomplete
                      selectedSkills={selectedSkills}
                      onSkillsChange={setSelectedSkills}
                    />
                  </div>
                  
                  {/* Benefits */}
                  <div>
                    <Label className="mb-2">Phúc lợi</Label>
                    <div className="flex flex-wrap gap-2">
                      {benefitOptions.map((benefit) => (
                        <Badge
                          key={benefit}
                          variant={selectedBenefits.includes(benefit) ? 'default' : 'outline'}
                          className="cursor-pointer"
                          onClick={() => {
                            if (selectedBenefits.includes(benefit)) {
                              setSelectedBenefits(selectedBenefits.filter(b => b !== benefit));
                            } else {
                              setSelectedBenefits([...selectedBenefits, benefit]);
                            }
                          }}
                        >
                          {benefit}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-4">
                    <Button onClick={handleApply} className="flex-1">
                      Áp dụng bộ lọc
                    </Button>
                    <Button onClick={handleClear} variant="outline">
                      Xóa tất cả
                    </Button>
                  </div>
                </div>
              )}
            </div>
          );
        }
        ```

- [ ] **Task 8: Skill Autocomplete Component (AC: 3)**
    - [ ] Create `frontend/features/jobs/components/SkillAutocomplete.tsx`:
        ```typescript
        'use client';
        
        import { useState, useEffect } from 'react';
        import { Input } from '@/components/ui/input';
        import { Badge } from '@/components/ui/badge';
        import { X } from 'lucide-react';
        import { getSkillSuggestionsAction } from '../actions';
        import { useDebounce } from '@/lib/hooks/useDebounce';
        
        interface SkillAutocompleteProps {
          selectedSkills: string[];
          onSkillsChange: (skills: string[]) => void;
        }
        
        export function SkillAutocomplete({ selectedSkills, onSkillsChange }: SkillAutocompleteProps) {
          const [input, setInput] = useState('');
          const [suggestions, setSuggestions] = useState([]);
          const [showSuggestions, setShowSuggestions] = useState(false);
          
          const debouncedInput = useDebounce(input, 300);
          
          useEffect(() => {
            if (debouncedInput.length >= 2) {
              fetchSuggestions(debouncedInput);
            } else {
              setSuggestions([]);
            }
          }, [debouncedInput]);
          
          const fetchSuggestions = async (query: string) => {
            const { data, error } = await getSkillSuggestionsAction(query);
            if (data) {
              setSuggestions(data);
              setShowSuggestions(true);
            }
          };
          
          const handleSelectSkill = (skill: string) => {
            if (!selectedSkills.includes(skill)) {
              onSkillsChange([...selectedSkills, skill]);
            }
            setInput('');
            setSuggestions([]);
            setShowSuggestions(false);
          };
          
          const handleRemoveSkill = (skill: string) => {
            onSkillsChange(selectedSkills.filter(s => s !== skill));
          };
          
          return (
            <div className="space-y-2">
              {/* Selected Skills */}
              {selectedSkills.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {selectedSkills.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                      <X
                        className="ml-1 h-3 w-3 cursor-pointer"
                        onClick={() => handleRemoveSkill(skill)}
                      />
                    </Badge>
                  ))}
                </div>
              )}
              
              {/* Input */}
              <div className="relative">
                <Input
                  placeholder="Nhập kỹ năng (e.g., Python, React)..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onFocus={() => setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                />
                
                {/* Suggestions Dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {suggestions.map((suggestion) => (
                      <div
                        key={suggestion.skill}
                        className="px-4 py-2 cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSelectSkill(suggestion.skill)}
                      >
                        <span className="font-medium">{suggestion.skill}</span>
                        <span className="text-sm text-gray-500 ml-2">
                          ({suggestion.count} jobs)
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        }
        ```

- [ ] **Task 9: Active Filter Tags Component (AC: 8)**
    - [ ] Create `frontend/features/jobs/components/ActiveFilters.tsx`:
        ```typescript
        interface ActiveFiltersProps {
          filters: AdvancedSearchFilters;
          onRemoveFilter: (filterKey: string, value?: string) => void;
          onClearAll: () => void;
        }
        
        export function ActiveFilters({ filters, onRemoveFilter, onClearAll }: ActiveFiltersProps) {
          const hasFilters = Object.values(filters).some(v => v !== undefined && v !== '');
          
          if (!hasFilters) return null;
          
          return (
            <div className="flex flex-wrap items-center gap-2 mb-4 p-4 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">Đang lọc:</span>
              
              {filters.minSalary && filters.maxSalary && (
                <Badge variant="secondary">
                  Lương: ${filters.minSalary} - ${filters.maxSalary}
                  <X className="ml-1 h-3 w-3 cursor-pointer" onClick={() => onRemoveFilter('salary')} />
                </Badge>
              )}
              
              {filters.jobTypes?.map((type) => (
                <Badge key={type} variant="secondary">
                  {type}
                  <X className="ml-1 h-3 w-3 cursor-pointer" onClick={() => onRemoveFilter('jobType', type)} />
                </Badge>
              ))}
              
              {filters.requiredSkills?.map((skill) => (
                <Badge key={skill} variant="secondary">
                  Skill: {skill}
                  <X className="ml-1 h-3 w-3 cursor-pointer" onClick={() => onRemoveFilter('skill', skill)} />
                </Badge>
              ))}
              
              {filters.benefits?.map((benefit) => (
                <Badge key={benefit} variant="secondary">
                  Benefit: {benefit}
                  <X className="ml-1 h-3 w-3 cursor-pointer" onClick={() => onRemoveFilter('benefit', benefit)} />
                </Badge>
              ))}
              
              <Button variant="ghost" size="sm" onClick={onClearAll}>
                Xóa tất cả
              </Button>
            </div>
          );
        }
        ```

- [ ] **Task 10: Update Search Page with Advanced Filters (AC: All)**
    - [ ] Update `frontend/app/jobs/search/page.tsx`:
        ```typescript
        'use client';
        
        import { useState, useEffect } from 'react';
        import { useRouter, useSearchParams } from 'next/navigation';
        import { AdvancedFilters } from '@/features/jobs/components/AdvancedFilters';
        import { ActiveFilters } from '@/features/jobs/components/ActiveFilters';
        import { JobCard } from '@/features/jobs/components/JobCard';
        import { Pagination } from '@/components/common/Pagination';
        import { searchJobsAction } from '@/features/jobs/actions';
        
        export default function JobSearchPage() {
          const router = useRouter();
          const searchParams = useSearchParams();
          
          // Parse URL params on mount
          const [filters, setFilters] = useState(() => ({
            keyword: searchParams.get('keyword') || '',
            location: searchParams.get('location') || '',
            minSalary: searchParams.get('min_salary') ? parseInt(searchParams.get('min_salary')) : undefined,
            maxSalary: searchParams.get('max_salary') ? parseInt(searchParams.get('max_salary')) : undefined,
            jobTypes: searchParams.getAll('job_types'),
            requiredSkills: searchParams.getAll('skills'),
            benefits: searchParams.getAll('benefits'),
          }));
          
          const [results, setResults] = useState(null);
          const [loading, setLoading] = useState(false);
          const [page, setPage] = useState(1);
          
          // Update URL when filters change
          const updateURL = (newFilters) => {
            const params = new URLSearchParams();
            if (newFilters.keyword) params.set('keyword', newFilters.keyword);
            if (newFilters.location) params.set('location', newFilters.location);
            if (newFilters.minSalary) params.set('min_salary', newFilters.minSalary.toString());
            if (newFilters.maxSalary) params.set('max_salary', newFilters.maxSalary.toString());
            newFilters.jobTypes?.forEach(t => params.append('job_types', t));
            newFilters.requiredSkills?.forEach(s => params.append('skills', s));
            newFilters.benefits?.forEach(b => params.append('benefits', b));
            
            router.push(`/jobs/search?${params.toString()}`, { scroll: false });
          };
          
          const handleSearch = async (newFilters, newPage = 1) => {
            setLoading(true);
            const { data, error } = await searchJobsAction({ ...newFilters, page: newPage });
            setLoading(false);
            
            if (data) {
              setResults(data);
              setPage(newPage);
            }
          };
          
          const handleApplyFilters = (advancedFilters) => {
            const newFilters = { ...filters, ...advancedFilters };
            setFilters(newFilters);
            updateURL(newFilters);
            handleSearch(newFilters, 1);
          };
          
          const handleRemoveFilter = (filterKey, value) => {
            const newFilters = { ...filters };
            // ... logic to remove specific filter
            setFilters(newFilters);
            updateURL(newFilters);
            handleSearch(newFilters, 1);
          };
          
          const handleClearAll = () => {
            const emptyFilters = { keyword: '', location: '' };
            setFilters(emptyFilters);
            router.push('/jobs/search');
            setResults(null);
          };
          
          return (
            <div className="container mx-auto py-8">
              <h1 className="text-3xl font-bold mb-6">Tìm kiếm việc làm</h1>
              
              {/* Basic Search Form (Story 9.1) */}
              {/* ... existing search form ... */}
              
              {/* Advanced Filters (Story 9.2) */}
              <AdvancedFilters
                onApplyFilters={handleApplyFilters}
                onClearFilters={handleClearAll}
              />
              
              {/* Active Filter Tags */}
              <ActiveFilters
                filters={filters}
                onRemoveFilter={handleRemoveFilter}
                onClearAll={handleClearAll}
              />
              
              {/* Results ... */}
            </div>
          );
        }
        ```

## Dev Notes

### Architecture Context

**Critical Coding Standards:**
- ✅ **SQLAlchemy Async**: Use eager loading (`selectinload`) for relationships
- ✅ **Array Operations**: Use PostgreSQL array operators (`overlap`, `contains`) with GIN indexes
- ✅ **Server Actions**: All filter changes must use Server Actions to preserve HttpOnly cookies
- ✅ **URL State Management**: Persist filter state in URL query params for bookmarking and sharing
- ✅ **DRY Principle**: Reuse existing components (Badge, Checkbox, Input) from shadcn/ui

### Database Schema Enhancement

**New Columns in `job_descriptions` table:**
```sql
-- Salary range (in USD for simplicity, could be currency-agnostic in future)
salary_min INTEGER,  -- e.g., 1000
salary_max INTEGER,  -- e.g., 3000

-- Job type (employment type)
job_type VARCHAR(50) CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance')),

-- Required skills (array of strings for MVP, could link to Skills table later)
required_skills TEXT[] DEFAULT '{}',  -- e.g., {'Python', 'React', 'SQL'}

-- Benefits (array of strings)
benefits TEXT[] DEFAULT '{}',  -- e.g., {'Health Insurance', 'Remote Work'}
```

**Migration Strategy:**
1. Create migration file: `alembic revision -m "add_advanced_search_fields_to_job_descriptions"`
2. Add columns with nullable constraints first
3. Backfill existing data (if needed) with default values
4. Add NOT NULL constraints if required
5. Add indexes for performance

**Index Strategy:**
- **Salary range**: B-tree composite index on `(salary_min, salary_max)` for range queries
- **Job type**: B-tree index for equality checks
- **Skills & Benefits**: GIN indexes for array containment queries

### API Specification Enhancement

**Endpoint:** `GET /api/v1/jobs/search/basic` (backward compatible with Story 9.1)

**New Query Parameters:**
- `min_salary` (optional): int, >= 0
- `max_salary` (optional): int, >= 0, must be >= min_salary
- `job_types` (optional): array of strings, max 5 items
- `required_skills` (optional): array of strings, max 20 items
- `benefits` (optional): array of strings, max 10 items

**Request Example:**
```http
GET /api/v1/jobs/search/basic?keyword=Python&min_salary=1000&max_salary=3000&job_types=full-time&job_types=contract&required_skills=Python&required_skills=React&benefits=Health%20Insurance
Cookie: access_token=<HttpOnly JWT>
```

**Response Schema (Enhanced):**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Senior Python Developer",
      "company_name": "recruiter@example.com",
      "location_type": "remote",
      "job_type": "full-time",
      "salary_min": 2000,
      "salary_max": 4000,
      "required_skills": ["Python", "Django", "PostgreSQL"],
      "benefits": ["Health Insurance", "Remote Work", "Learning Budget"],
      "posted_date": "2 days ago",
      "description_snippet": "We are looking for..."
    }
  ],
  "total_count": 15,
  "page": 1,
  "total_pages": 2
}
```

**New Endpoint:** `GET /api/v1/jobs/skills/autocomplete`
- Returns skill suggestions based on existing job data
- Includes count of how many jobs require each skill
- Used for autocomplete feature in skill filter

### Technical Decisions

**1. Filter Logic - AND vs OR:**

| Filter Type | Logic | Rationale |
|------------|-------|-----------|
| Keyword + Location | AND | User wants jobs matching BOTH criteria |
| Job Types | OR | User is flexible with employment type |
| Skills | OR | User has ANY of these skills |
| Benefits | AND | User wants ALL these benefits |

**Example:**
```
User searches: keyword="Python" + job_types=["full-time", "contract"] + skills=["Python", "React"] + benefits=["Remote Work", "Health Insurance"]

SQL WHERE clause:
  (title ILIKE '%Python%' OR description ILIKE '%Python%')  -- keyword (OR)
  AND job_type IN ('full-time', 'contract')                 -- job types (OR within IN)
  AND (required_skills && ARRAY['Python', 'React'])         -- skills (OR via overlap)
  AND benefits @> ARRAY['Remote Work']                      -- benefit 1 (AND)
  AND benefits @> ARRAY['Health Insurance']                 -- benefit 2 (AND)
```

**2. Salary Range Filtering - Overlap Logic:**

User wants jobs with salary range that **overlaps** with their desired range:

```python
# User wants: $1000 - $3000
# Match these jobs:
# ✓ Job A: $800 - $2000   (overlaps: $1000-$2000)
# ✓ Job B: $2000 - $4000  (overlaps: $2000-$3000)
# ✓ Job C: $1500 - $2500  (completely within range)
# ✗ Job D: $3500 - $5000  (no overlap)

# SQL Implementation:
WHERE (
  (salary_min IS NOT NULL AND salary_min >= user_min AND salary_max <= user_max)
  OR
  (salary_max IS NOT NULL AND salary_max >= user_min)
)
```

**3. Skills Autocomplete - Performance:**

Use `unnest()` to flatten array column into rows, then aggregate:
```sql
SELECT unnest(required_skills) AS skill, COUNT(*) AS count
FROM job_descriptions
WHERE is_active = TRUE
  AND unnest(required_skills) ILIKE '%Python%'
GROUP BY skill
ORDER BY count DESC
LIMIT 10;
```

**Trade-off:** This query can be slow on large datasets. Consider caching suggestions or pre-computing skill counts.

**4. URL State Persistence:**

Store all filter values in URL query parameters:
- ✅ Allows bookmarking search results
- ✅ Enables sharing search URLs
- ✅ Preserves filters on page refresh
- ⚠️ Long URLs with many filters (acceptable trade-off)

**5. Mobile UX - Collapsed Filters:**

On mobile (< 768px), collapse advanced filters by default:
- Saves vertical space
- User can expand when needed
- Desktop: expand by default for discoverability

### Component Hierarchy

```
app/jobs/search/page.tsx (Client Component)
├── BasicSearchForm (Story 9.1)
│   ├── Input - Keyword
│   ├── Input - Location
│   └── Button - Search
├── AdvancedFilters (Story 9.2 - NEW)
│   ├── ChevronDown/Up - Toggle expand
│   ├── Input - Min/Max Salary
│   ├── Checkbox[] - Job Types
│   ├── SkillAutocomplete - Skills
│   │   ├── Input - Search skills
│   │   ├── Dropdown - Suggestions
│   │   └── Badge[] - Selected skills
│   ├── Badge[] - Benefits
│   ├── Button - Apply Filters
│   └── Button - Clear All
├── ActiveFilters (Story 9.2 - NEW)
│   ├── Badge[] - Active filter tags
│   └── Button - Clear All
├── JobCard[] (Story 9.1 - Enhanced)
│   ├── Title, company, location (existing)
│   ├── Job type, salary range (NEW)
│   └── Skills, benefits (NEW)
└── Pagination (Story 9.1)
```

### Error Handling Strategy

**Backend:**
1. **Salary validation**: Pydantic validator ensures `max_salary >= min_salary`
2. **Array size limits**: Prevent abuse by limiting array sizes (max 20 skills, 10 benefits)
3. **Invalid enum values**: Job type must be in predefined list
4. **Database errors**: Log and return 500 with generic message

**Frontend:**
1. **Salary input validation**: Show error if max < min before submission
2. **API errors**: Toast notification with retry option
3. **Empty autocomplete**: Show "No suggestions found" message
4. **URL parsing errors**: Fallback to empty filters if URL params are invalid

### Testing Strategy

**Backend Tests:**
- **Unit tests** (`test_search_service.py`):
  - Test each filter independently
  - Test combined filters (all at once)
  - Test filter logic (AND vs OR)
  - Test salary overlap logic
  - Test skill autocomplete
  - Test edge cases (empty arrays, null values)
- **Integration tests** (`test_job_router.py`):
  - Test API endpoint with real database
  - Test parameter validation (salary range, array limits)
  - Test query param parsing (arrays as repeated params)

**Frontend Tests:**
- **Component tests**:
  - Test AdvancedFilters expand/collapse
  - Test SkillAutocomplete suggestions
  - Test ActiveFilters tag rendering and removal
  - Test filter state updates
- **Integration tests**:
  - Test URL state persistence
  - Test filter + pagination interaction
  - Test clear all filters functionality

### Performance Considerations

**Database Performance:**
1. **GIN Indexes**: Essential for array containment queries
   - `required_skills`: GIN index enables fast `&&` (overlap) operator
   - `benefits`: GIN index enables fast `@>` (contains) operator
2. **Query Optimization**:
   - Use `selectinload` to avoid N+1 queries on recruiter relationship
   - Index on `(salary_min, salary_max)` for range queries
3. **Expected Load**:
   - MVP: < 5,000 job descriptions
   - Concurrent searches: < 100 per minute
   - Target response time: < 800ms (slightly slower than Story 9.1 due to more filters)

**Frontend Performance:**
1. **Debounced Autocomplete**: Wait 300ms after user stops typing before fetching suggestions
2. **URL Updates**: Use `router.push` with `{ scroll: false }` to prevent page jump
3. **Filter State**: Store in React state, not re-fetch on every filter change

### Future Enhancements (Out of Scope for 9.2)

**Story 9.3 will add:**
- Semantic search using pgvector (AI-powered job matching)
- "Save Search" functionality with email alerts
- Sort options (relevance, date, salary)

**Story 9.4 will add:**
- One-click job application
- Application tracking dashboard
- Resume matching score per job

### Dependencies

**Backend:**
- No new dependencies required (PostgreSQL array support is built-in)

**Frontend:**
- `lucide-react` - Already installed (ChevronDown, ChevronUp, X icons)
- Consider adding `react-select` for better multi-select UX (OPTIONAL)

### Checklist Before Dev Starts

- [ ] Run Story 9.1 implementation and verify it works
- [ ] Verify `job_descriptions` table exists
- [ ] Verify PostgreSQL version supports GIN indexes (9.4+)
- [ ] Verify `useDebounce` hook exists in `/lib/hooks` (or create it)
- [ ] Review Story 9.1 code to understand integration points
- [ ] Read `coding-standards.md` for SQLAlchemy async and array operations

### Reference Files

**Backend:**
- `backend/app/modules/jobs/models.py` - JobDescription model (UPDATE)
- `backend/app/modules/jobs/schemas.py` - API schemas (UPDATE)
- `backend/app/modules/jobs/service.py` - Business logic (UPDATE)
- `backend/app/modules/jobs/router.py` - API endpoints (UPDATE)
- `backend/alembic/versions/` - Migration files (NEW)

**Frontend:**
- `frontend/app/jobs/search/page.tsx` - Search page (UPDATE from Story 9.1)
- `frontend/features/jobs/actions.ts` - Server Actions (UPDATE)
- `frontend/features/jobs/components/AdvancedFilters.tsx` - Advanced filters panel (NEW)
- `frontend/features/jobs/components/SkillAutocomplete.tsx` - Skill autocomplete (NEW)
- `frontend/features/jobs/components/ActiveFilters.tsx` - Active filter tags (NEW)
- `frontend/features/jobs/components/JobCard.tsx` - Job card (UPDATE - show new fields)
- `frontend/lib/hooks/useDebounce.ts` - Debounce hook (NEW or existing)

**Architecture:**
- `_bmad-output/planning-artifacts/architecture/coding-standards.md` - SQLAlchemy async rules
- `_bmad-output/planning-artifacts/architecture/database-schema.md` - Schema patterns
- `_bmad-output/implementation-artifacts/9-1-tim-kiem-tin-tuyen-dung-co-ban.md` - Story 9.1 reference

### Git Commit Pattern Reference

Based on recent commits:
```
feat(jobs): Add advanced filtering to job search

- Add salary range, job type, skills, and benefits filters to job_descriptions table
- Create database migration with GIN indexes for array columns
- Enhance search_jobs() service to support advanced filters
- Add skill autocomplete endpoint for suggestions
- Create AdvancedFilters component with expandable panel
- Create SkillAutocomplete component with debounced suggestions
- Create ActiveFilters component for showing active filter tags
- Update JobSearchPage to integrate advanced filters with URL state
- Add unit and integration tests for all new filtering logic
- Update JobCard to display salary, job type, skills, and benefits

Closes #9.2
```

## Definition of Done

- [ ] All acceptance criteria (AC1-AC8) are met and verified
- [ ] Database migration created and applied (new columns + indexes)
- [ ] All backend tasks (1-5) completed with passing tests
- [ ] All frontend tasks (6-10) completed and render correctly
- [ ] Code follows project coding standards (async patterns, array operations)
- [ ] Unit tests written and passing (> 80% coverage for new code)
- [ ] Integration tests written and passing
- [ ] No regressions in Story 9.1 functionality (backward compatible)
- [ ] API endpoint backward compatible (existing queries still work)
- [ ] Filter state persists in URL and survives page refresh
- [ ] Mobile responsive design tested (collapsed filters on mobile)
- [ ] Autocomplete performance tested (< 200ms response time)
- [ ] Search with all filters tested (< 800ms response time)
- [ ] Peer code review completed
- [ ] Manual testing completed on dev environment

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Debug Log References
_To be filled by dev agent_

### Completion Notes List
_To be filled by dev agent_

### File List
_To be filled by dev agent_
