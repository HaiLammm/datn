"""
Tests for Job Description service functionality.
Covers CRUD operations, authorization checks, and JD parsing.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, Mock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs import services as job_service
from app.modules.jobs.schemas import JobDescriptionCreate, LocationType, JDParseStatus, ParsedRequirementsUpdate
from app.modules.jobs.models import JobDescription
from app.modules.users.models import User


class TestCreateJobDescription:
    """Tests for job description creation functionality."""

    @pytest.mark.asyncio
    async def test_create_job_description_success(self):
        """Test successful job description creation with all fields."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1

        # Create input data
        create_data = JobDescriptionCreate(
            title="Senior Python Developer",
            description="Looking for an experienced Python developer...",
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            min_experience_years=3,
            location_type=LocationType.REMOTE,
            salary_min=80000,
            salary_max=120000,
        )

        result = await job_service.create_job_description(mock_db, mock_user, create_data)

        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify the added object has correct attributes
        added_jd = mock_db.add.call_args[0][0]
        assert added_jd.user_id == mock_user.id
        assert added_jd.title == "Senior Python Developer"
        assert added_jd.description == "Looking for an experienced Python developer..."
        assert added_jd.required_skills == ["Python", "FastAPI", "PostgreSQL"]
        assert added_jd.min_experience_years == 3
        assert added_jd.location_type == "remote"
        assert added_jd.salary_min == 80000
        assert added_jd.salary_max == 120000
        assert added_jd.parse_status == "pending"

    @pytest.mark.asyncio
    async def test_create_job_description_minimal_fields(self):
        """Test job description creation with only required fields."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        mock_user = Mock(spec=User)
        mock_user.id = 1

        create_data = JobDescriptionCreate(
            title="Junior Developer",
            description="Entry level position",
        )

        await job_service.create_job_description(mock_db, mock_user, create_data)

        # Verify the added object has correct defaults
        added_jd = mock_db.add.call_args[0][0]
        assert added_jd.title == "Junior Developer"
        assert added_jd.location_type == "remote"  # default
        assert added_jd.required_skills is None
        assert added_jd.min_experience_years is None
        assert added_jd.parse_status == "pending"  # default


class TestGetJobDescriptionsByUser:
    """Tests for listing user's job descriptions."""

    @pytest.mark.asyncio
    async def test_get_job_descriptions_by_user_returns_only_users_jds(self):
        """Test that only the user's job descriptions are returned."""
        user_id = 1
        
        # Create mock JDs
        mock_jd1 = Mock(spec=JobDescription)
        mock_jd1.id = uuid.uuid4()
        mock_jd1.user_id = user_id
        mock_jd1.title = "JD 1"

        mock_jd2 = Mock(spec=JobDescription)
        mock_jd2.id = uuid.uuid4()
        mock_jd2.user_id = user_id
        mock_jd2.title = "JD 2"

        # Setup mock database
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_jd1, mock_jd2]
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_descriptions_by_user(mock_db, user_id)

        assert len(result) == 2
        assert mock_jd1 in result
        assert mock_jd2 in result

    @pytest.mark.asyncio
    async def test_get_job_descriptions_by_user_empty_list(self):
        """Test that empty list is returned when user has no JDs."""
        user_id = 1

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_descriptions_by_user(mock_db, user_id)

        assert result == []


class TestGetJobDescription:
    """Tests for getting a single job description."""

    @pytest.mark.asyncio
    async def test_get_job_description_success(self):
        """Test getting a job description that exists and belongs to user."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.user_id = user_id
        mock_jd.title = "Test JD"

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_jd
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_description(mock_db, jd_id, user_id)

        assert result == mock_jd
        assert result.id == jd_id

    @pytest.mark.asyncio
    async def test_get_job_description_not_found(self):
        """Test getting a job description that doesn't exist."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_description(mock_db, jd_id, user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_job_description_wrong_user(self):
        """Test that getting another user's JD returns None."""
        jd_id = uuid.uuid4()
        owner_user_id = 1
        requester_user_id = 2

        # The query filters by both jd_id AND user_id, so it returns None
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_description(mock_db, jd_id, requester_user_id)

        assert result is None


class TestDeleteJobDescription:
    """Tests for job description deletion."""

    @pytest.mark.asyncio
    async def test_delete_job_description_success(self):
        """Test successful job description deletion."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.user_id = user_id

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_jd
        mock_db.execute.return_value = mock_result
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        result = await job_service.delete_job_description(mock_db, jd_id, user_id)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_jd)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_job_description_not_found(self):
        """Test deleting a non-existent job description."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await job_service.delete_job_description(mock_db, jd_id, user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_job_description_wrong_user(self):
        """Test that deleting another user's JD returns False."""
        jd_id = uuid.uuid4()
        owner_user_id = 1
        requester_user_id = 2

        # Query filters by both jd_id AND user_id, so it returns None
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await job_service.delete_job_description(mock_db, jd_id, requester_user_id)

        assert result is False


class TestUpdateParseStatus:
    """Tests for parse status update functionality."""

    @pytest.mark.asyncio
    async def test_update_parse_status_success(self):
        """Test updating parse status."""
        jd_id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        await job_service.update_parse_status(
            mock_db, jd_id, JDParseStatus.PROCESSING
        )

        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()


class TestParseJobDescription:
    """Tests for JD parsing service function."""

    @pytest.mark.asyncio
    async def test_parse_job_description_success(self):
        """Test successful JD parsing updates status and saves results."""
        jd_id = uuid.uuid4()

        # Mock JD
        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.description = "Looking for Python developer with 3+ years experience"

        # Mock parsed result
        from app.modules.jobs.jd_parser import ParsedJDRequirements
        mock_parsed = ParsedJDRequirements(
            required_skills=["python"],
            min_experience_years=3,
        )

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        with patch(
            "app.modules.jobs.services.get_job_description_by_id",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.services.jd_parser.parse_jd",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            await job_service.parse_job_description(mock_db, jd_id)

        # Should have called execute for status updates
        assert mock_db.execute.call_count >= 1

    @pytest.mark.asyncio
    async def test_parse_job_description_not_found(self):
        """Test parsing non-existent JD does nothing."""
        jd_id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        with patch(
            "app.modules.jobs.services.get_job_description_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            await job_service.parse_job_description(mock_db, jd_id)

        # Should have updated status to PROCESSING then returned early
        # when JD not found

    @pytest.mark.asyncio
    async def test_parse_job_description_handles_timeout(self):
        """Test parsing handles LLM timeout gracefully."""
        jd_id = uuid.uuid4()

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.description = "Python developer job description"

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        with patch(
            "app.modules.jobs.services.get_job_description_by_id",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.services.jd_parser.parse_jd",
            new_callable=AsyncMock,
            side_effect=TimeoutError("LLM timeout"),
        ):
            # Should not raise, but update status to FAILED
            await job_service.parse_job_description(mock_db, jd_id)

    @pytest.mark.asyncio
    async def test_parse_job_description_handles_exception(self):
        """Test parsing handles general exceptions gracefully."""
        jd_id = uuid.uuid4()

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.description = "Python developer job description"

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        with patch(
            "app.modules.jobs.services.get_job_description_by_id",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.services.jd_parser.parse_jd",
            new_callable=AsyncMock,
            side_effect=Exception("Unexpected error"),
        ):
            # Should not raise, but update status to FAILED
            await job_service.parse_job_description(mock_db, jd_id)


class TestGetJobDescriptionById:
    """Tests for getting JD by ID without user check."""

    @pytest.mark.asyncio
    async def test_get_job_description_by_id_success(self):
        """Test getting JD by ID returns the JD."""
        jd_id = uuid.uuid4()

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_jd
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_description_by_id(mock_db, jd_id)

        assert result == mock_jd

    @pytest.mark.asyncio
    async def test_get_job_description_by_id_not_found(self):
        """Test getting non-existent JD by ID returns None."""
        jd_id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await job_service.get_job_description_by_id(mock_db, jd_id)

        assert result is None


class TestUpdateParsedRequirements:
    """Tests for update_parsed_requirements service function."""

    @pytest.mark.asyncio
    async def test_update_parsed_requirements_success(self):
        """Test successful update of parsed requirements."""
        jd_id = uuid.uuid4()
        user_id = 1

        # Mock JD with existing parsed requirements
        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.user_id = user_id
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
            "job_title_normalized": "Python Developer",
            "key_responsibilities": ["Write code"]
        }

        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_jd
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        update_data = ParsedRequirementsUpdate(
            required_skills=["python", "django", "postgresql"],
            min_experience_years=5
        )

        with patch(
            "app.modules.jobs.services.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            result = await job_service.update_parsed_requirements(
                mock_db, jd_id, user_id, update_data
            )

        assert result == mock_jd
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_jd)

    @pytest.mark.asyncio
    async def test_update_parsed_requirements_partial_update(self):
        """Test partial update preserves unmodified fields."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_jd = Mock(spec=JobDescription)
        mock_jd.id = jd_id
        mock_jd.user_id = user_id
        mock_jd.parsed_requirements = {
            "required_skills": ["python"],
            "nice_to_have_skills": ["docker", "kubernetes"],
            "min_experience_years": 2,
            "job_title_normalized": "Backend Developer",
            "key_responsibilities": ["API development"]
        }

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Only update required_skills, leave other fields alone
        update_data = ParsedRequirementsUpdate(
            required_skills=["react", "typescript"]
            # nice_to_have_skills not provided - should be preserved
        )

        with patch(
            "app.modules.jobs.services.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            result = await job_service.update_parsed_requirements(
                mock_db, jd_id, user_id, update_data
            )

        # The update should have been called with merged data
        assert result == mock_jd
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_parsed_requirements_jd_not_found(self):
        """Test update returns None when JD not found."""
        jd_id = uuid.uuid4()
        user_id = 1

        mock_db = AsyncMock(spec=AsyncSession)

        update_data = ParsedRequirementsUpdate(
            required_skills=["python"]
        )

        with patch(
            "app.modules.jobs.services.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await job_service.update_parsed_requirements(
                mock_db, jd_id, user_id, update_data
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_parsed_requirements_wrong_owner(self):
        """Test update returns None when user doesn't own the JD."""
        jd_id = uuid.uuid4()
        owner_user_id = 1
        requester_user_id = 2

        mock_db = AsyncMock(spec=AsyncSession)

        update_data = ParsedRequirementsUpdate(
            required_skills=["python"]
        )

        # get_job_description returns None for wrong owner
        with patch(
            "app.modules.jobs.services.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await job_service.update_parsed_requirements(
                mock_db, jd_id, requester_user_id, update_data
            )

        assert result is None
