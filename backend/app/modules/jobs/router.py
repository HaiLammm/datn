import mimetypes
import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.core.database import get_db, AsyncSessionLocal
from app.modules.auth.dependencies import get_current_user
from app.modules.jobs import services as job_service
from app.modules.jobs.schemas import (
    CandidateCVFromSearchResponse,
    JDParseStatus,
    JDParseStatusResponse,
    JobDescriptionCreate,
    JobDescriptionList,
    JobDescriptionResponse,
    LocationType,
    MatchBreakdownResponse,
    ParsedJDRequirements,
    ParsedQueryResponse,
    ParsedRequirementsUpdate,
    RankedCandidateListResponse,
    RankedCandidateResponse,
    RecruiterCVAccessResponse,
    SearchResultListResponse,
    SearchResultResponse,
    SemanticSearchRequest,
)
from app.modules.jobs.candidate_ranker import candidate_ranker
from app.modules.jobs.semantic_searcher import semantic_searcher
from app.modules.users.models import User
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter()


async def _run_jd_parsing(jd_id: UUID) -> None:
    """
    Background task wrapper for JD parsing.
    
    Creates its own database session since background tasks
    run after the request completes.
    """
    async with AsyncSessionLocal() as db:
        await job_service.parse_job_description(db, jd_id)


@router.post(
    "/jd",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job description",
)
async def create_job_description(
    data: JobDescriptionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    """
    Create a new job description for the authenticated user.

    The JD will be parsed asynchronously in the background after creation.
    Check the parse_status field or use the /parse-status endpoint to monitor progress.

    - **title**: Job title (required)
    - **description**: Full job description (required)
    - **required_skills**: List of required skills (optional)
    - **min_experience_years**: Minimum years of experience (optional)
    - **location_type**: One of 'remote', 'hybrid', 'on-site' (default: 'remote')
    - **salary_min**: Minimum salary (optional)
    - **salary_max**: Maximum salary (optional)
    """
    jd = await job_service.create_job_description(db, current_user, data)
    
    # Trigger background parsing (non-blocking)
    background_tasks.add_task(_run_jd_parsing, jd.id)
    
    return JobDescriptionResponse.model_validate(jd)


@router.post(
    "/jd/upload",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job description from file upload",
)
async def create_job_description_from_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or DOCX file containing the job description"),
    title: str = Form(..., min_length=1, max_length=255, description="Job title"),
    location_type: str = Form(default="remote", description="Work location type: remote, hybrid, on-site"),
    required_skills: Optional[List[str]] = Form(default=None, description="List of required skills"),
    min_experience_years: Optional[int] = Form(default=None, ge=0, description="Minimum years of experience"),
    salary_min: Optional[int] = Form(default=None, ge=0, description="Minimum salary"),
    salary_max: Optional[int] = Form(default=None, ge=0, description="Maximum salary"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    """
    Create a new job description by uploading a PDF or DOCX file.
    
    The file content will be extracted and used as the job description text.
    The JD will be parsed asynchronously in the background after creation.
    
    - **file**: PDF or DOCX file (required, max 10MB)
    - **title**: Job title (required)
    - **location_type**: One of 'remote', 'hybrid', 'on-site' (default: 'remote')
    - **required_skills**: List of required skills (optional)
    - **min_experience_years**: Minimum years of experience (optional)
    - **salary_min**: Minimum salary (optional)
    - **salary_max**: Maximum salary (optional)
    """
    # Validate file type
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file PDF hoặc DOCX.",
        )
    
    # Validate file size (10MB max)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước file tối đa là 10MB.",
        )
    # Reset file position for later use
    await file.seek(0)
    
    # Validate location_type
    try:
        location = LocationType(location_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"location_type phải là một trong: remote, hybrid, on-site. Nhận được: {location_type}",
        )
    
    # Extract text from file
    jd = await job_service.create_job_description_from_file(
        db=db,
        user=current_user,
        file=file,
        title=title,
        location_type=location,
        required_skills=required_skills,
        min_experience_years=min_experience_years,
        salary_min=salary_min,
        salary_max=salary_max,
    )
    
    # Trigger background parsing (non-blocking)
    background_tasks.add_task(_run_jd_parsing, jd.id)
    
    return JobDescriptionResponse.model_validate(jd)


@router.get(
    "/jd",
    response_model=JobDescriptionList,
    summary="List all job descriptions for current user",
)
async def list_job_descriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionList:
    """
    Get all job descriptions created by the authenticated user.
    """
    jds = await job_service.get_job_descriptions_by_user(db, current_user.id)
    return JobDescriptionList(
        items=[JobDescriptionResponse.model_validate(jd) for jd in jds],
        total=len(jds),
    )


@router.get(
    "/jd/{jd_id}",
    response_model=JobDescriptionResponse,
    summary="Get a specific job description",
)
async def get_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    """
    Get a specific job description by ID.
    Only returns the job description if it belongs to the authenticated user.
    """
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    return JobDescriptionResponse.model_validate(jd)


@router.get(
    "/jd/{jd_id}/parse-status",
    response_model=JDParseStatusResponse,
    summary="Get JD parsing status",
)
async def get_parse_status(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JDParseStatusResponse:
    """
    Get the parsing status and results for a specific job description.
    
    Returns:
    - **jd_id**: Job description ID
    - **parse_status**: One of 'pending', 'processing', 'completed', 'failed'
    - **parsed_requirements**: Extracted requirements (null if not yet parsed)
    """
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # Convert parsed_requirements dict to schema if present
    parsed_req = None
    if jd.parsed_requirements:
        parsed_req = ParsedJDRequirements.model_validate(jd.parsed_requirements)
    
    return JDParseStatusResponse(
        jd_id=jd.id,
        parse_status=jd.parse_status,
        parsed_requirements=parsed_req,
        parse_error=jd.parse_error,
    )


@router.patch(
    "/jd/{jd_id}/parsed-requirements",
    response_model=JDParseStatusResponse,
    summary="Update parsed requirements",
)
async def update_parsed_requirements(
    jd_id: UUID,
    data: ParsedRequirementsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JDParseStatusResponse:
    """
    Update the parsed requirements for a job description.
    
    Allows partial updates to:
    - **required_skills**: List of required skill names
    - **nice_to_have_skills**: List of optional skill names
    - **min_experience_years**: Minimum years of experience
    
    Requirements:
    - JD must exist and belong to the authenticated user
    - JD parse_status must be 'completed' (can only edit after successful parsing)
    
    Unchanged fields (e.g., job_title_normalized, key_responsibilities) are preserved.
    """
    # Check JD exists and belongs to user
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # Check if JD parsing is complete
    if jd.parse_status != JDParseStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update parsed requirements: JD parsing is not completed. Current status: {jd.parse_status}",
        )
    
    # Update parsed requirements
    updated_jd = await job_service.update_parsed_requirements(
        db, jd_id, current_user.id, data
    )
    
    # Convert parsed_requirements dict to schema
    parsed_req = None
    if updated_jd and updated_jd.parsed_requirements:
        parsed_req = ParsedJDRequirements.model_validate(updated_jd.parsed_requirements)
    
    return JDParseStatusResponse(
        jd_id=jd_id,
        parse_status=JDParseStatus.COMPLETED.value,
        parsed_requirements=parsed_req,
        parse_error=None,
    )


@router.post(
    "/jd/{jd_id}/reparse",
    response_model=JDParseStatusResponse,
    summary="Trigger JD re-parsing",
)
async def reparse_job_description(
    jd_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JDParseStatusResponse:
    """
    Trigger re-parsing of an existing job description.
    
    Useful when:
    - Previous parsing failed
    - JD content was updated
    - You want to refresh parsed requirements
    """
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # Reset status to pending and trigger parsing
    await job_service.update_parse_status(db, jd_id, JDParseStatus.PENDING)
    background_tasks.add_task(_run_jd_parsing, jd_id)
    
    return JDParseStatusResponse(
        jd_id=jd.id,
        parse_status=JDParseStatus.PENDING.value,
        parsed_requirements=None,
    )


@router.delete(
    "/jd/{jd_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job description",
)
async def delete_job_description(
    jd_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a specific job description by ID.
    Only deletes the job description if it belongs to the authenticated user.
    """
    deleted = await job_service.delete_job_description(db, jd_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )


@router.get(
    "/jd/{jd_id}/candidates",
    response_model=RankedCandidateListResponse,
    summary="Get ranked candidates for a job description",
)
async def get_candidates_for_jd(
    jd_id: UUID,
    limit: int = 20,
    offset: int = 0,
    min_score: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RankedCandidateListResponse:
    """
    Get candidates ranked by match score for a specific job description.
    
    The JD must have completed parsing before candidates can be ranked.
    
    Query Parameters:
    - **limit**: Maximum number of candidates to return (default: 20, max: 100)
    - **offset**: Number of candidates to skip for pagination (default: 0)
    - **min_score**: Minimum match score to include (0-100, default: 0)
    
    Returns:
    - **items**: List of ranked candidates with match details
    - **total**: Total number of matching candidates (before pagination)
    - **limit**: Applied limit
    - **offset**: Applied offset
    """
    # Validate parameters
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100
    
    if offset < 0:
        offset = 0
    
    if min_score < 0:
        min_score = 0
    elif min_score > 100:
        min_score = 100
    
    # Check JD exists and belongs to user
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # Check if JD parsing is complete
    if jd.parse_status != JDParseStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"JD parsing not complete. Current status: {jd.parse_status}",
        )
    
    try:
        # Get ranked candidates
        candidates, total = await candidate_ranker.rank_candidates(
            db=db,
            jd_id=jd_id,
            limit=limit,
            offset=offset,
            min_score=min_score,
        )
        
        # Convert to response schema
        items = [
            RankedCandidateResponse(
                cv_id=c.cv_id,
                user_id=c.user_id,
                match_score=c.match_score,
                breakdown=MatchBreakdownResponse(
                    matched_skills=c.breakdown.matched_skills,
                    missing_skills=c.breakdown.missing_skills,
                    extra_skills=c.breakdown.extra_skills,
                    skill_score=c.breakdown.skill_score,
                    experience_score=c.breakdown.experience_score,
                    experience_years=c.breakdown.experience_years,
                ),
                cv_summary=c.cv_summary,
                filename=c.filename,
                is_public=c.is_public,
            )
            for c in candidates
        ]
        
        return RankedCandidateListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/search",
    response_model=SearchResultListResponse,
    summary="Search candidates using natural language",
)
async def search_candidates(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResultListResponse:
    """
    Search for candidates using a natural language query.
    
    This endpoint allows searching for candidates without uploading a full JD.
    The query is parsed to extract skills and keywords, then matched against
    CV data.
    
    **Request Body:**
    - **query**: Natural language search query (required, min 2 chars)
      - Examples: "Python developer with AWS experience"
      - "Senior fullstack engineer 5 years React"
      - "Lập trình viên Python có kinh nghiệm Docker"
    - **limit**: Maximum results to return (default: 20, max: 100)
    - **offset**: Results to skip for pagination (default: 0)
    - **min_score**: Minimum relevance score 0-100 (default: 0)
    
    **Returns:**
    - **items**: List of matching candidates with relevance scores
    - **total**: Total number of matching candidates
    - **parsed_query**: Information about how the query was parsed
    
    **Scoring Algorithm:**
    - Skill Match (70%): Ratio of matched skills to query skills
    - Keyword Match (30%): Keyword presence in CV content
    """
    # Validate query
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters long",
        )
    
    # Clamp parameters
    limit = min(max(request.limit, 1), 100)
    offset = max(request.offset, 0)
    min_score = min(max(request.min_score, 0), 100)
    
    try:
        # Perform search
        results, total = await semantic_searcher.search_candidates(
            query=request.query,
            db=db,
            limit=limit,
            offset=offset,
            min_score=min_score,
        )
        
        # Get parsed query info from searcher
        parsed = await semantic_searcher._parse_query(request.query)
        
        # Convert to response schema
        items = [
            SearchResultResponse(
                cv_id=r.cv_id,
                user_id=r.user_id,
                relevance_score=r.relevance_score,
                matched_skills=r.matched_skills,
                cv_summary=r.cv_summary,
                filename=r.filename,
            )
            for r in results
        ]
        
        return SearchResultListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            parsed_query=ParsedQueryResponse(
                extracted_skills=parsed.extracted_skills,
                experience_keywords=parsed.experience_keywords,
                raw_query=parsed.raw_query,
            ),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get(
    "/candidates/{cv_id}",
    response_model=CandidateCVFromSearchResponse,
    summary="Get CV details from search results (no JD context)",
)
async def get_candidate_cv_from_search(
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CandidateCVFromSearchResponse:
    """
    Get CV analysis details for a candidate from search results.
    
    This endpoint is used when viewing a candidate found via semantic search,
    without a specific JD context for matching.
    
    **Requirements:**
    - User must be authenticated (recruiter)
    - The CV must be public (is_public = true)
    
    **Returns:**
    - CV analysis including AI score, summary, skills, and breakdown
    - No match context (no JD to compare against)
    
    **Errors:**
    - 404: CV not found or inactive
    - 403: CV is private (is_public = false)
    """
    # 1. Fetch CV with analysis
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()
    
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # 2. Check if CV is active (not soft-deleted)
    if not cv.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # 3. Check if CV is public
    if not cv.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CV is private. Contact candidate directly.",
        )
    
    # 4. Get analysis data
    analysis = cv.analyses[0] if cv.analyses else None
    
    return CandidateCVFromSearchResponse(
        cv_id=cv.id,
        filename=cv.filename,
        uploaded_at=cv.uploaded_at,
        ai_score=analysis.ai_score if analysis else None,
        ai_summary=analysis.ai_summary if analysis else None,
        extracted_skills=analysis.extracted_skills if analysis else None,
        skill_breakdown=analysis.skill_breakdown if analysis else None,
        skill_categories=analysis.skill_categories if analysis else None,
        is_public=cv.is_public,
    )


@router.get(
    "/candidates/{cv_id}/file",
    summary="Get CV file from search results (no JD context)",
    responses={
        200: {
            "description": "CV file for viewing or download",
            "content": {"application/pdf": {}, "application/octet-stream": {}},
        },
        403: {"description": "CV is private"},
        404: {"description": "CV not found"},
    },
)
async def get_candidate_cv_file_from_search(
    cv_id: UUID,
    download: bool = Query(False, description="If true, return as attachment for download"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Get the original CV file for a candidate from search results.
    
    **Requirements:**
    - User must be authenticated (recruiter)
    - The CV must be public (is_public = true)
    
    **Query Parameters:**
    - **download**: If true, returns file as attachment for download. 
                   Default: false (inline for preview)
    
    **Returns:**
    - CV file as StreamingResponse with appropriate content-type
    
    **Errors:**
    - 404: CV not found or inactive
    - 403: CV is private (is_public = false)
    """
    # 1. Fetch CV
    result = await db.execute(
        select(CV).where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()
    
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # 2. Check if CV is active (not soft-deleted)
    if not cv.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Store file info before any potential session issues
    cv_file_path = cv.file_path
    cv_filename = cv.filename
    cv_is_public = cv.is_public
    
    # 3. Check if CV is public
    if not cv_is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CV is private. Cannot access file.",
        )
    
    # 4. Verify file exists on disk
    cv_path = Path(cv_file_path)
    if cv_path.is_absolute():
        full_path = cv_path
    elif cv_file_path.startswith("data/cv_uploads/"):
        full_path = Path(cv_file_path)
    else:
        full_path = settings.CV_STORAGE_PATH / cv_file_path
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV file not found on server",
        )
    
    # 5. Determine content type
    content_type, _ = mimetypes.guess_type(cv_filename)
    if content_type is None:
        content_type = "application/octet-stream"
    
    # 6. Set content disposition
    if download:
        content_disposition = f'attachment; filename="{cv_filename}"'
    else:
        content_disposition = f'inline; filename="{cv_filename}"'
    
    # 7. Create file iterator for streaming
    def file_iterator():
        with open(full_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_iterator(),
        media_type=content_type,
        headers={
            "Content-Disposition": content_disposition,
        },
    )


@router.get(
    "/jd/{jd_id}/candidates/{cv_id}",
    response_model=RecruiterCVAccessResponse,
    summary="Get full CV details for a candidate (recruiter access)",
)
async def get_candidate_cv_for_recruiter(
    jd_id: UUID,
    cv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecruiterCVAccessResponse:
    """
    Get full CV analysis details for a specific candidate.
    
    **Requirements:**
    - The JD must belong to the authenticated user (recruiter)
    - The CV must have been matched with this JD (via candidate ranking)
    - The CV must be public (is_public = true)
    
    **Returns:**
    - Full CV analysis including AI score, summary, skills, and breakdown
    - Match context (score and matched skills) for this JD
    
    **Errors:**
    - 404: JD or CV not found, or CV was not matched with this JD
    - 403: CV is private (is_public = false)
    """
    # 1. Verify JD exists and belongs to current user
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # 2. Fetch CV with analysis
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()
    
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this JD",
        )
    
    # 2.1. Check if CV is active (not soft-deleted)
    if not cv.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this JD",
        )
    
    # 3. Check if CV is public
    if not cv.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CV is private. Contact candidate directly.",
        )
    
    # 4. Get the match context by re-ranking this specific CV
    # This ensures the CV was indeed matched with this JD
    try:
        candidates, _ = await candidate_ranker.rank_candidates(
            db=db,
            jd_id=jd_id,
            limit=1000,  # Get all to find this specific CV
            offset=0,
            min_score=0,
        )
        
        # Find this CV in the ranked candidates
        candidate_match = next(
            (c for c in candidates if c.cv_id == cv_id),
            None
        )
        
        if candidate_match is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found for this JD",
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # 5. Get analysis data
    analysis = cv.analyses[0] if cv.analyses else None
    
    return RecruiterCVAccessResponse(
        cv_id=cv.id,
        filename=cv.filename,
        uploaded_at=cv.uploaded_at,
        ai_score=analysis.ai_score if analysis else None,
        ai_summary=analysis.ai_summary if analysis else None,
        extracted_skills=analysis.extracted_skills if analysis else None,
        skill_breakdown=analysis.skill_breakdown if analysis else None,
        skill_categories=analysis.skill_categories if analysis else None,
        match_score=candidate_match.match_score,
        matched_skills=candidate_match.breakdown.matched_skills,
    )


@router.get(
    "/jd/{jd_id}/candidates/{cv_id}/file",
    summary="Get CV file for a candidate (recruiter access)",
    responses={
        200: {
            "description": "CV file for viewing or download",
            "content": {"application/pdf": {}, "application/octet-stream": {}},
        },
        403: {"description": "CV is private"},
        404: {"description": "JD or CV not found"},
    },
)
async def get_candidate_cv_file_for_recruiter(
    jd_id: UUID,
    cv_id: UUID,
    download: bool = Query(False, description="If true, return as attachment for download"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Get the original CV file for a specific candidate.
    
    **Requirements:**
    - The JD must belong to the authenticated user (recruiter)
    - The CV must have been matched with this JD (via candidate ranking)
    - The CV must be public (is_public = true)
    
    **Query Parameters:**
    - **download**: If true, returns file as attachment for download. 
                   Default: false (inline for preview)
    
    **Returns:**
    - CV file as StreamingResponse with appropriate content-type
    
    **Errors:**
    - 404: JD or CV not found, or CV was not matched with this JD
    - 403: CV is private (is_public = false)
    """
    # 1. Verify JD exists and belongs to current user
    jd = await job_service.get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )
    
    # 2. Fetch CV
    result = await db.execute(
        select(CV).where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()
    
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this JD",
        )
    
    # 2.1. Check if CV is active (not soft-deleted)
    if not cv.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this JD",
        )
    
    # Store file info before any potential session issues
    cv_file_path = cv.file_path
    cv_filename = cv.filename
    cv_is_public = cv.is_public
    
    # 3. Check if CV is public
    if not cv_is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CV is private. Cannot access file.",
        )
    
    # 4. Verify CV was matched with this JD
    try:
        candidates, _ = await candidate_ranker.rank_candidates(
            db=db,
            jd_id=jd_id,
            limit=1000,
            offset=0,
            min_score=0,
        )
        
        candidate_match = next(
            (c for c in candidates if c.cv_id == cv_id),
            None
        )
        
        if candidate_match is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found for this JD",
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # 5. Verify file exists on disk
    # Handle file path resolution:
    # - file_path in DB may be "data/cv_uploads/xxx.pdf" (relative from project root)
    # - or just "xxx.pdf" (filename only, older format)
    # - or absolute path
    cv_path = Path(cv_file_path)
    if cv_path.is_absolute():
        full_path = cv_path
    elif cv_file_path.startswith("data/cv_uploads/"):
        # Already includes the storage path prefix, use from project root
        full_path = Path(cv_file_path)
    else:
        # Just filename, prepend storage path
        full_path = settings.CV_STORAGE_PATH / cv_file_path
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV file not found on server",
        )
    
    # 6. Determine content type
    content_type, _ = mimetypes.guess_type(cv_filename)
    if content_type is None:
        content_type = "application/octet-stream"
    
    # 7. Set content disposition
    if download:
        content_disposition = f'attachment; filename="{cv_filename}"'
    else:
        content_disposition = f'inline; filename="{cv_filename}"'
    
    # 8. Create file iterator for streaming
    def file_iterator():
        with open(full_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_iterator(),
        media_type=content_type,
        headers={
            "Content-Disposition": content_disposition,
        },
    )
