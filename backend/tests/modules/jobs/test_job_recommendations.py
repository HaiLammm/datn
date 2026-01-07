import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient
from uuid import uuid4

from app.modules.jobs import services as job_service
from app.modules.jobs.models import JobDescription
from app.modules.jobs.schemas import JobRecommendationResponse
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis
from app.modules.users.models import User

# Mock external services
@pytest.fixture
def mock_embedding_service():
    with patch("app.modules.jobs.services.embedding_service") as mock:
        mock.is_available = True
        mock.generate_embedding.return_value = [0.1] * 384
        yield mock

@pytest.fixture
def mock_vector_store():
    with patch("app.modules.jobs.services.vector_store") as mock:
        yield mock

@pytest.fixture
def mock_skill_matcher():
    with patch("app.modules.jobs.services.SkillMatcher") as MockMatcher:
        instance = MockMatcher.return_value
        instance.match_skills.return_value = {
            "skill_match_rate": 0.5,
            "matched_skills": ["Python"],
            "missing_skills": ["Java"]
        }
        yield instance

@pytest.mark.asyncio
async def test_get_recommendations_no_cv(async_client: AsyncClient, test_user: User, mock_db_session):
    """Test recommendations when user has no active CV."""
    from app.main import app
    from app.modules.auth.dependencies import require_job_seeker, get_current_user
    from unittest.mock import MagicMock
    
    # Create a job seeker user
    job_seeker = User(id=999, email="seeker@test.com", role="job_seeker", is_active=True)
    
    # Override dependencies
    app.dependency_overrides[require_job_seeker] = lambda: job_seeker
    app.dependency_overrides[get_current_user] = lambda: job_seeker
    
    # Mock DB result for CV query (return None)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    try:
        response = await async_client.get("/api/v1/jobs/recommendations")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        pass

@pytest.mark.asyncio
async def test_get_recommendations_success(
    async_client: AsyncClient,
    test_user: User,
    mock_db_session,
    mock_embedding_service,
    mock_vector_store,
    mock_skill_matcher
):
    """Test successful recommendations flow."""
    from app.main import app
    from app.modules.auth.dependencies import require_job_seeker, get_current_user
    from unittest.mock import MagicMock
    from datetime import datetime

    # Create a job seeker user
    job_seeker = User(id=999, email="seeker@test.com", role="job_seeker", is_active=True)
    
    # 1. Setup Data Objects
    cv = CV(
        id=uuid4(),
        user_id=job_seeker.id,
        filename="test_cv.pdf",
        file_path="path/to/test_cv.pdf",
        is_active=True
    )
    
    analysis = CVAnalysis(
        id=uuid4(),
        cv_id=cv.id,
        status="COMPLETED",
        extracted_skills=["Python", "FastAPI"],
        ai_summary="Experienced Python Developer"
    )
    cv.analyses = [analysis] # Manually link for mock return
    
    jd1 = JobDescription(
        id=uuid4(),
        user_id=1,
        title="Python Developer",
        description="We need a Python dev",
        location_type="remote",
        is_active=True,
        parse_status="completed",
        parsed_requirements={"required_skills": ["Python"]},
        salary_min=1000,
        salary_max=2000,
        uploaded_at=datetime.now()
    )
    
    # 2. Configure DB Mock Sequence
    # Call 1: Get CV
    cv_result = MagicMock()
    cv_result.scalar_one_or_none.return_value = cv
    
    # Call 2: Get JDs
    jd_result = MagicMock()
    jd_result.scalars.return_value.all.return_value = [jd1]
    
    mock_db_session.execute.side_effect = [cv_result, jd_result]
    
    # 3. Mock Vector Search Results
    mock_vector_store.query_similar.return_value = [
        {"id": str(jd1.id), "score": 0.9, "metadata": {}}
    ]
    
    # 4. Override Auth
    app.dependency_overrides[require_job_seeker] = lambda: job_seeker
    app.dependency_overrides[get_current_user] = lambda: job_seeker
    
    # 5. Call Endpoint
    response = await async_client.get("/api/v1/jobs/recommendations")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(jd1.id)
    assert data[0]["match_score"] > 0
    
    # Verify mock usage
    mock_embedding_service.generate_embedding.assert_called_once()
    mock_vector_store.query_similar.assert_called_once()
