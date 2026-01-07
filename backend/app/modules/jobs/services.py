import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import func, select, update, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.jobs.models import JobDescription, Application
from app.modules.jobs.schemas import JobDescriptionCreate, JDParseStatus, LocationType, ParsedRequirementsUpdate, JobRecommendationResponse
from app.modules.jobs.jd_parser import jd_parser
from app.modules.users.models import User
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis
from app.modules.ai.skill_scorer import SkillMatcher
from app.modules.ai.vector_store import vector_store
from app.modules.ai.embeddings import embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


async def create_job_description(
    db: AsyncSession, user: User, data: JobDescriptionCreate
) -> JobDescription:
    """Create a new job description for the given user."""
    # Capture user.id before any async operations to avoid MissingGreenlet error
    # when User object is from a different session
    user_id = user.id
    
    db_jd = JobDescription(
        user_id=user_id,
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        min_experience_years=data.min_experience_years,
        location_type=data.location_type.value,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        parse_status=JDParseStatus.PENDING.value,
    )
    db.add(db_jd)
    await db.commit()
    await db.refresh(db_jd)
    logger.info("Created job description %s for user %s", db_jd.id, user_id)
    return db_jd


async def create_job_description_from_file(
    db: AsyncSession,
    user: User,
    file: UploadFile,
    title: str,
    location_type: LocationType,
    required_skills: Optional[List[str]] = None,
    min_experience_years: Optional[int] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
) -> JobDescription:
    """
    Create a new job description from an uploaded file.
    
    Extracts text from PDF/DOCX file and creates a JobDescription record.
    """
    from app.modules.ai.service import ai_service
    
    # Capture user.id before any async operations
    user_id = user.id
    
    # Get file extension
    file_extension = Path(file.filename).suffix.lower() if file.filename else ".pdf"
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Extract text from file
        description = await ai_service.perform_ocr_extraction(tmp_path)
        
        if not description or len(description.strip()) < 10:
            raise ValueError("Không thể trích xuất nội dung từ file. Vui lòng kiểm tra file hoặc sử dụng paste văn bản.")
        
        logger.info("Extracted %d characters from file %s", len(description), file.filename)
        
    finally:
        # Clean up temp file
        try:
            Path(tmp_path).unlink()
        except Exception as e:
            logger.warning("Failed to delete temp file %s: %s", tmp_path, e)
    
    # Create JobDescription record
    db_jd = JobDescription(
        user_id=user_id,
        title=title,
        description=description,
        required_skills=required_skills,
        min_experience_years=min_experience_years,
        location_type=location_type.value,
        salary_min=salary_min,
        salary_max=salary_max,
        parse_status=JDParseStatus.PENDING.value,
    )
    db.add(db_jd)
    await db.commit()
    await db.refresh(db_jd)
    logger.info("Created job description %s from file %s for user %s", db_jd.id, file.filename, user_id)
    return db_jd


async def get_job_descriptions_by_user(
    db: AsyncSession, user_id: int
) -> List[JobDescription]:
    """Get all job descriptions for a specific user."""
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == user_id)
        .order_by(JobDescription.uploaded_at.desc())
    )
    return list(result.scalars().all())


async def get_job_description(
    db: AsyncSession, jd_id: UUID, user_id: int
) -> Optional[JobDescription]:
    """
    Get a job description by ID with user ownership check.
    Returns None if not found or user doesn't own it.
    """
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id, JobDescription.user_id == user_id
        )
    )
    return result.scalars().first()


async def delete_job_description(
    db: AsyncSession, jd_id: UUID, user_id: int
) -> bool:
    """
    Delete a job description with user ownership check.
    Returns True if deleted, False if not found or user doesn't own it.
    """
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == jd_id, JobDescription.user_id == user_id
        )
    )
    jd = result.scalars().first()
    if jd is None:
        return False

    await db.delete(jd)
    await db.commit()
    logger.info("Deleted job description %s for user %s", jd_id, user_id)
    return True


async def get_job_description_by_id(
    db: AsyncSession, jd_id: UUID
) -> Optional[JobDescription]:
    """
    Get a job description by ID without user ownership check.
    Used for background tasks that need to access JD by ID.
    """
    result = await db.execute(
        select(JobDescription).where(JobDescription.id == jd_id)
    )
    return result.scalars().first()


async def update_parse_status(
    db: AsyncSession, jd_id: UUID, status: JDParseStatus, parse_error: str | None = None
) -> None:
    """
    Update the parse status of a job description.
    
    Args:
        db: Database session.
        jd_id: Job description ID.
        status: New parse status.
        parse_error: Error message if status is FAILED.
    """
    values = {"parse_status": status.value}
    if parse_error is not None:
        values["parse_error"] = parse_error
    elif status == JDParseStatus.COMPLETED:
        # Clear error on success
        values["parse_error"] = None
    
    stmt = (
        update(JobDescription)
        .where(JobDescription.id == jd_id)
        .values(**values)
    )
    await db.execute(stmt)
    await db.commit()
    logger.debug(f"Updated JD {jd_id} parse_status to {status.value}")


async def parse_job_description(db: AsyncSession, jd_id: UUID) -> None:
    """
    Parse a job description and extract structured requirements.
    
    This function:
    1. Updates status to PROCESSING
    2. Calls JDParser to extract requirements
    3. Saves parsed results to database
    4. Updates status to COMPLETED or FAILED
    
    Args:
        db: Database session.
        jd_id: Job description ID to parse.
    """
    logger.info(f"Starting JD parsing for {jd_id}")
    
    try:
        # Step 1: Update status to PROCESSING
        await update_parse_status(db, jd_id, JDParseStatus.PROCESSING)
        
        # Step 2: Fetch the JD
        jd = await get_job_description_by_id(db, jd_id)
        if jd is None:
            logger.error(f"JD {jd_id} not found for parsing")
            return
        
        # Step 3: Parse the JD description
        parsed_result = await jd_parser.parse_jd(jd.description)
        
        # Step 4: Save parsed results
        stmt = (
            update(JobDescription)
            .where(JobDescription.id == jd_id)
            .values(
                parsed_requirements=parsed_result.to_dict(),
                parse_status=JDParseStatus.COMPLETED.value,
            )
        )
        await db.execute(stmt)
        await db.commit()
        
        logger.info(
            f"JD {jd_id} parsed successfully: "
            f"{len(parsed_result.required_skills)} required skills, "
            f"{len(parsed_result.nice_to_have_skills)} nice-to-have skills"
        )
        
    except TimeoutError as e:
        error_msg = f"LLM timeout: {str(e)}"
        logger.error(f"JD parsing timeout for {jd_id}: {e}")
        await update_parse_status(db, jd_id, JDParseStatus.FAILED, error_msg)
        
    except Exception as e:
        error_msg = f"Parsing error: {str(e)[:200]}"
        logger.error(f"JD parsing failed for {jd_id}: {e}")
        await update_parse_status(db, jd_id, JDParseStatus.FAILED, error_msg)


async def update_parsed_requirements(
    db: AsyncSession,
    jd_id: UUID,
    user_id: int,
    data: ParsedRequirementsUpdate
) -> Optional[JobDescription]:
    """
    Update parsed requirements for a job description.
    
    Only updates fields that are provided (not None).
    Preserves existing fields like job_title_normalized and key_responsibilities.
    
    Args:
        db: Database session.
        jd_id: Job description ID.
        user_id: User ID for ownership check.
        data: Update data with optional fields.
        
    Returns:
        Updated JobDescription or None if not found/not owned.
    """
    # Get JD with ownership check
    jd = await get_job_description(db, jd_id, user_id)
    if jd is None:
        return None
    
    # Merge with existing parsed_requirements
    current = jd.parsed_requirements or {}
    update_dict = data.model_dump(exclude_none=True)
    
    merged = {**current, **update_dict}
    
    # Update in database
    stmt = (
        update(JobDescription)
        .where(JobDescription.id == jd_id)
        .values(parsed_requirements=merged)
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(jd)
    
    logger.info(f"Updated parsed requirements for JD {jd_id}")
    return jd


async def calculate_job_match_score(
    db: AsyncSession,
    job_id: UUID,
    cv_id: UUID,
    user_id: int
) -> Tuple[int, Optional[str]]:
    """
    Calculate job match score for a CV against a JD.

    Story 5.7: This endpoint calculates a job match score prioritizing
    JD skill requirements over the general CV quality score.

    Args:
        db: Database session.
        job_id: Job description ID.
        cv_id: CV ID to calculate match for.
        user_id: User ID for ownership check of JD.

    Returns:
        Tuple of (match_score: int 0-100, error: Optional[str])
        If error is not None, match_score will be 0.

    Scoring Algorithm:
        - Skill Match (70%): Percentage of JD required skills found in CV
        - Experience Match (30%): Based on years of experience vs JD requirements
    """
    logger.info(f"Calculating job match score for CV {cv_id} against JD {job_id}")

    # 1. Verify JD exists and belongs to user
    jd = await get_job_description(db, job_id, user_id)
    if jd is None:
        return 0, "Job description not found"

    # 2. Check if JD parsing is complete
    if jd.parse_status != JDParseStatus.COMPLETED.value:
        return 0, f"JD parsing not complete. Current status: {jd.parse_status}"

    # 3. Fetch CV with analysis
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()

    if cv is None:
        return 0, "CV not found"

    if not cv.is_active:
        return 0, "CV not found"

    if not cv.is_public:
        return 0, "CV is private"

    # 4. Get CV analysis
    analysis = cv.analyses[0] if cv.analyses else None
    if analysis is None:
        return 0, "CV has not been analyzed"

    # 5. Get CV skills from analysis
    cv_skill_categories = analysis.skill_categories or {}

    # 6. Get JD requirements
    parsed_req = jd.parsed_requirements or {}
    jd_required_skills = parsed_req.get("required_skills", [])
    jd_nice_to_have = parsed_req.get("nice_to_have_skills", [])
    jd_min_experience = parsed_req.get("min_experience_years")

    # 7. Calculate skill match using SkillMatcher
    matcher = SkillMatcher()

    # Build JD text from requirements for skill extraction
    jd_skills_text = " ".join(jd_required_skills + jd_nice_to_have)

    # If no skills in parsed requirements, use the full JD description
    if not jd_skills_text.strip():
        jd_skills_text = jd.description

    match_result = matcher.match_skills(cv_skill_categories, jd_skills_text)

    # 8. Calculate skill score (0-70 points)
    skill_match_rate = match_result["skill_match_rate"]
    skill_score = int(skill_match_rate * 70)

    # 9. Calculate experience score (0-30 points)
    experience_score = 0

    # Get CV experience years from ai_feedback.experience_breakdown.total_years
    # This is where Ollama stores the experience years after analysis
    cv_experience_years = None
    ai_feedback = analysis.ai_feedback or {}
    experience_breakdown = ai_feedback.get("experience_breakdown", {})
    if isinstance(experience_breakdown, dict) and "total_years" in experience_breakdown:
        try:
            cv_experience_years = float(experience_breakdown.get("total_years"))
        except (ValueError, TypeError):
            pass

    if jd_min_experience is not None and jd_min_experience > 0:
        if cv_experience_years is not None:
            if cv_experience_years >= jd_min_experience:
                # Full points if meets or exceeds requirement
                experience_score = 30
            elif cv_experience_years > 0:
                # Partial score based on ratio
                ratio = cv_experience_years / jd_min_experience
                experience_score = int(ratio * 30)
            # else: 0 points if no experience
        else:
            # No experience data available - give middle score
            experience_score = 15
    else:
        # No experience requirement in JD - give full points
        experience_score = 30

    # 10. Calculate total score
    total_score = skill_score + experience_score
    total_score = min(100, max(0, total_score))  # Clamp to 0-100

    logger.info(
        f"Job match score for CV {cv_id} against JD {job_id}: "
        f"total={total_score}, skill={skill_score} (rate={skill_match_rate:.2%}), "
        f"experience={experience_score}"
    )

    return total_score, None


async def get_skill_suggestions(
    db: AsyncSession, query: str, limit: int = 10
) -> List[dict]:
    """
    Get skill suggestions based on jobs' required_skills.
    
    Returns a list of dicts with 'skill' and 'count' keys.
    """
    # Create subquery to unnest skills from active jobs
    unnest_stmt = select(func.unnest(JobDescription.required_skills).label("skill")).where(
        JobDescription.is_active == True
    )
    subq = unnest_stmt.subquery()
    
    # Query for skills matching the keyword, grouped and counted
    stmt = (
        select(subq.c.skill, func.count().label("count"))
        .where(subq.c.skill.ilike(f"%{query}%"))
        .group_by(subq.c.skill)
        .order_by(func.count().desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return [{"skill": row.skill, "count": row.count} for row in result.all()]


async def search_jobs_basic(
    db: AsyncSession,
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    job_types: Optional[List[str]] = None,
    skills: Optional[List[str]] = None,
    benefits: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[JobDescription], int]:
    """
    Basic job search for job seekers with advanced filters.
    
    Args:
        db: Database session.
        keyword: Search keyword to match in title or description (case-insensitive).
        location: Location type filter (remote, hybrid, on-site).
        min_salary: Minimum salary filter.
        max_salary: Maximum salary filter.
        job_types: List of job types to filter (OR logic).
        limit: Maximum number of results to return.
        offset: Number of results to skip for pagination.
        
    Returns:
        Tuple of (list of matching jobs, total count before pagination).
    """
    # Build base query for active jobs only
    query = select(JobDescription).where(JobDescription.is_active == True)
    
    # Apply keyword filter (search in title and description)
    if keyword and keyword.strip():
        search_pattern = f"%{keyword.strip()}%"
        query = query.where(
            (JobDescription.title.ilike(search_pattern)) |
            (JobDescription.description.ilike(search_pattern))
        )
    
    # Apply location filter
    if location:
        query = query.where(JobDescription.location_type == location.lower())
        
    # Apply job type filter (OR logic)
    if job_types and len(job_types) > 0:
        # Normalize job types to lowercase
        normalized_types = [t.lower() for t in job_types]
        query = query.where(JobDescription.job_type.in_(normalized_types))
        
    # Apply salary range filter (Overlap logic)
    if min_salary is not None or max_salary is not None:
        if min_salary is not None and max_salary is not None:
            # Match if job range overlaps with user range
            # Job Max >= User Min AND Job Min <= User Max
            query = query.where(
                and_(
                    JobDescription.salary_max >= min_salary,
                    JobDescription.salary_min <= max_salary
                )
            )
        elif min_salary is not None:
            # Only min is provided: overlap with [min, infinity]
            # Job Max >= User Min
            query = query.where(JobDescription.salary_max >= min_salary)
        elif max_salary is not None:
            # Only max is provided: overlap with [0, max]
            # Job Min <= User Max
            query = query.where(JobDescription.salary_min <= max_salary)

    # Apply skills filter (Overlap: match any skill)
    if skills:
        # Use Postgres overlap operator (&&)
        query = query.where(JobDescription.required_skills.overlap(skills))

    # Apply benefits filter (Overlap: match any benefit)
    if benefits:
        query = query.where(JobDescription.benefits.overlap(benefits))
    
    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(JobDescription.uploaded_at.desc())
    query = query.limit(limit).offset(offset)
    
    # Execute query
    result = await db.execute(query)
    jobs = list(result.scalars().all())
    
    logger.info(
        f"Basic job search: keyword='{keyword}', location='{location}', "
        f"found {total} jobs, returning {len(jobs)} (limit={limit}, offset={offset})"
    )
    
    return jobs, total


async def get_public_job(db: AsyncSession, job_id: UUID) -> Optional[JobDescription]:
    """Get active job details."""
    query = select(JobDescription).where(
        JobDescription.id == job_id,
        JobDescription.is_active == True
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_application(
    db: AsyncSession, job_id: UUID, user_id: int, cv_id: UUID, cover_letter: Optional[str] = None
) -> Application:
    """Submit an application."""
    # Check job
    job = await get_public_job(db, job_id)
    if not job:
        raise ValueError("Job not found or inactive")

    # Check duplicate
    query = select(Application).where(
        Application.job_id == job_id,
        Application.user_id == user_id
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise ValueError("You have already applied to this job")

    # Verify CV exists and belongs to user
    cv_query = select(CV).where(CV.id == cv_id, CV.user_id == user_id)
    cv_result = await db.execute(cv_query)
    if not cv_result.scalar_one_or_none():
         raise ValueError("Invalid CV")

    application = Application(
        job_id=job_id,
        user_id=user_id,
        cv_id=cv_id,
        cover_letter=cover_letter,
        status="pending"
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_recommendations_for_user(
    db: AsyncSession, user_id: int, limit: int = 10
) -> List[JobRecommendationResponse]:
    """
    Get personalized job recommendations for a user.
    
    Algorithm:
    1. Get user's active/latest public CV
    2. Generate embedding for CV content
    3. Semantic Search (Vector Store): Retrieve top 50 candidates
    4. Hybrid Scoring for each candidate:
       - Skills Match (40%): Overlap of structured skills
       - Experience Match (30%): Years of experience check
       - Location Match (15%): Remote preference or location match
       - Semantic Match (15%): Vector similarity score
       
    Returns:
        List of JobRecommendationResponse objects sorted by match_score.
    """
    # 1. Get User's Active CV
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.user_id == user_id, CV.is_active == True)
        .order_by(CV.uploaded_at.desc())
        .limit(1)
    )
    cv = result.scalar_one_or_none()
    
    # If no CV, return empty (Frontend should show "Upload CV" CTA)
    if not cv:
        return []
        
    # Get CV Analysis content for embedding
    cv_content = ""
    cv_skills = []
    cv_experience_years = 0.0
    
    if cv.analyses and cv.analyses[0].status == "COMPLETED":
        analysis = cv.analyses[0]
        # Use AI summary and extracted skills for better semantic representation
        cv_content = f"Skills: {', '.join(analysis.extracted_skills or [])}\n"
        cv_content += f"Summary: {analysis.ai_summary or ''}\n"
        
        cv_skills = analysis.extracted_skills or []
        
        # Extract experience years
        ai_feedback = analysis.ai_feedback or {}
        exp_breakdown = ai_feedback.get("experience_breakdown", {})
        if isinstance(exp_breakdown, dict):
            cv_experience_years = float(exp_breakdown.get("total_years", 0))
    else:
        # Fallback to simple file path or name if analysis pending (suboptimal)
        cv_content = cv.filename
        
    # 2. Generate Embedding
    if not embedding_service.is_available:
        logger.warning("Embedding service unavailable for recommendations")
        return []
        
    query_embedding = embedding_service.generate_embedding(cv_content)
    if not query_embedding:
        return []
        
    # 3. Semantic Search
    # Query more than limit to allow regarding based on other factors
    vector_results = vector_store.query_similar(
        collection_name=settings.CHROMA_COLLECTION_JOBS,
        query_embedding=query_embedding,
        top_k=50
    )
    
    if not vector_results:
        return []
        
    # extract JD IDs from vector results
    jd_ids = [UUID(r['id']) for r in vector_results]
    jd_score_map = {UUID(r['id']): r['score'] for r in vector_results} # semantic score 0-1
    
    # 4. Fetch JD Details
    # Fetch active jobs only
    jd_result = await db.execute(
        select(JobDescription)
        .where(
            JobDescription.id.in_(jd_ids),
            JobDescription.is_active == True,
            JobDescription.parse_status == JDParseStatus.COMPLETED.value
        )
    )
    jds = jd_result.scalars().all()
    
    recommendations = []
    skill_matcher = SkillMatcher()
    
    for jd in jds:
        # --- CALCULATION ---
        
        # A. Semantic Score (15%)
        # Normalize vector score (usually 0.0-1.0 cosine similarity)
        semantic_score = jd_score_map.get(jd.id, 0.0)
        weighted_semantic = semantic_score * 15
        
        # B. Skills Match (40%)
        # Reuse logic similar to calculate_job_match_score but avoid DB calls
        parsed_req = jd.parsed_requirements or {}
        jd_required = parsed_req.get("required_skills", [])
        jd_nice = parsed_req.get("nice_to_have_skills", [])
        
        # Use SkillMatcher for robust matching
        jd_skills_text = " ".join(jd_required + jd_nice)
        if not jd_skills_text.strip():
            jd_skills_text = jd.description or ""
            
        # We need categories for matcher, but if detailed categories missing, 
        # just pass extracted skills as a generic list wrapped in dict if needed
        # Actually SkillMatcher.match_skills takes (cv_skill_categories, jd_text)
        # We can construct a simple category dict if needed, or if cv analysis has it
        cv_categories = {}
        if cv.analyses:
            cv_categories = cv.analyses[0].skill_categories or {}
            
        if not cv_categories and cv_skills:
            cv_categories = {"general": cv_skills}
            
        match_result = skill_matcher.match_skills(cv_categories, jd_skills_text)
        skill_match_rate = match_result["skill_match_rate"] # 0.0 to 1.0
        weighted_skills = skill_match_rate * 40
        
        # C. Experience Match (30%)
        jd_min_exp = jd.min_experience_years
        exp_score_val = 0.0
        
        if jd_min_exp is not None and jd_min_exp > 0:
            if cv_experience_years >= jd_min_exp:
                exp_score_val = 1.0
            elif cv_experience_years > 0:
                exp_score_val = cv_experience_years / jd_min_exp
        else:
            exp_score_val = 1.0 # No requirement met
            
        weighted_experience = exp_score_val * 30
        
        # D. Location Match (15%)
        # Simplified: Remote = 100%, else 50% (neutral)
        loc_score_val = 0.5
        if jd.location_type == "remote":
            loc_score_val = 1.0
        weighted_location = loc_score_val * 15
        
        # TOTAL SCORE
        total_score = weighted_skills + weighted_experience + weighted_location + weighted_semantic
        total_score = min(100, max(0, int(total_score)))
        
        # Match Breakdown
        matched_skills = match_result.get("matched_skills", [])
        missing_skills = match_result.get("missing_skills", [])
        
        recommendations.append(JobRecommendationResponse(
            id=jd.id,
            title=jd.title,
            description=jd.description,
            location_type=jd.location_type,
            salary_min=jd.salary_min,
            salary_max=jd.salary_max,
            match_score=total_score,
            semantic_score=semantic_score,
            matched_skills=matched_skills[:10],
            missing_skills=missing_skills[:10],
            uploaded_at=jd.uploaded_at
        ))
        
    # Sort by score descending
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    return recommendations[:limit]
