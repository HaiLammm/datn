import logging
import tempfile
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models import JobDescription
from app.modules.jobs.schemas import JobDescriptionCreate, JDParseStatus, LocationType, ParsedRequirementsUpdate
from app.modules.jobs.jd_parser import jd_parser
from app.modules.users.models import User

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
