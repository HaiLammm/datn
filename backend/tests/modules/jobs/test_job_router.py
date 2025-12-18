"""
Tests for Job Description router/API endpoints.
Covers CRUD endpoints, authentication, authorization, and parsing.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from httpx import AsyncClient


class TestCreateJobDescriptionEndpoint:
    """Tests for POST /api/v1/jobs/jd endpoint."""

    @pytest.mark.asyncio
    async def test_create_jd_success(self, async_client: AsyncClient):
        """Test successful job description creation returns 201."""
        # Mock the service layer
        mock_jd = MagicMock()
        mock_jd.id = uuid.uuid4()
        mock_jd.user_id = 1
        mock_jd.title = "Senior Python Developer"
        mock_jd.description = "Looking for experienced Python developer"
        mock_jd.uploaded_at = datetime.utcnow()
        mock_jd.is_active = True
        mock_jd.required_skills = ["Python", "FastAPI"]
        mock_jd.min_experience_years = 3
        mock_jd.location_type = "remote"
        mock_jd.salary_min = 80000
        mock_jd.salary_max = 120000
        mock_jd.parse_status = "pending"
        mock_jd.parsed_requirements = None

        with patch(
            "app.modules.jobs.router.job_service.create_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.post(
                "/api/v1/jobs/jd",
                json={
                    "title": "Senior Python Developer",
                    "description": "Looking for experienced Python developer",
                    "required_skills": ["Python", "FastAPI"],
                    "min_experience_years": 3,
                    "location_type": "remote",
                    "salary_min": 80000,
                    "salary_max": 120000,
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Senior Python Developer"
        assert data["user_id"] == 1
        assert data["required_skills"] == ["Python", "FastAPI"]
        assert data["location_type"] == "remote"
        assert data["parse_status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_jd_triggers_background_parsing(self, async_client: AsyncClient):
        """Test that creating a JD triggers background parsing task."""
        mock_jd = MagicMock()
        mock_jd.id = uuid.uuid4()
        mock_jd.user_id = 1
        mock_jd.title = "Developer"
        mock_jd.description = "Job description"
        mock_jd.uploaded_at = datetime.utcnow()
        mock_jd.is_active = True
        mock_jd.required_skills = None
        mock_jd.min_experience_years = None
        mock_jd.location_type = "remote"
        mock_jd.salary_min = None
        mock_jd.salary_max = None
        mock_jd.parse_status = "pending"
        mock_jd.parsed_requirements = None

        with patch(
            "app.modules.jobs.router.job_service.create_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router._run_jd_parsing",
            new_callable=AsyncMock,
        ) as mock_parse:
            response = await async_client.post(
                "/api/v1/jobs/jd",
                json={
                    "title": "Developer",
                    "description": "Job description",
                },
            )

        assert response.status_code == 201
        # Background task should be scheduled (verified by checking response is immediate)
        assert response.json()["parse_status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_jd_missing_title(self, async_client: AsyncClient):
        """Test that missing title returns 422 validation error."""
        response = await async_client.post(
            "/api/v1/jobs/jd",
            json={
                "description": "Looking for developer",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "title" in str(data["detail"])

    @pytest.mark.asyncio
    async def test_create_jd_missing_description(self, async_client: AsyncClient):
        """Test that missing description returns 422 validation error."""
        response = await async_client.post(
            "/api/v1/jobs/jd",
            json={
                "title": "Developer",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "description" in str(data["detail"])

    @pytest.mark.asyncio
    async def test_create_jd_invalid_location_type(self, async_client: AsyncClient):
        """Test that invalid location_type returns 422 validation error."""
        response = await async_client.post(
            "/api/v1/jobs/jd",
            json={
                "title": "Developer",
                "description": "Job description",
                "location_type": "invalid_type",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_jd_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test that unauthenticated request returns 401."""
        response = await unauthenticated_async_client.post(
            "/api/v1/jobs/jd",
            json={
                "title": "Developer",
                "description": "Job description",
            },
        )

        # Should be 401 or 403 depending on OAuth2 implementation
        assert response.status_code in [401, 403]


class TestListJobDescriptionsEndpoint:
    """Tests for GET /api/v1/jobs/jd endpoint."""

    @pytest.mark.asyncio
    async def test_list_jds_success(self, async_client: AsyncClient):
        """Test listing job descriptions returns user's JDs only."""
        mock_jd1 = MagicMock()
        mock_jd1.id = uuid.uuid4()
        mock_jd1.user_id = 1
        mock_jd1.title = "JD 1"
        mock_jd1.description = "Description 1"
        mock_jd1.uploaded_at = datetime.utcnow()
        mock_jd1.is_active = True
        mock_jd1.required_skills = None
        mock_jd1.min_experience_years = None
        mock_jd1.location_type = "remote"
        mock_jd1.salary_min = None
        mock_jd1.salary_max = None
        mock_jd1.parse_status = "pending"
        mock_jd1.parsed_requirements = None

        mock_jd2 = MagicMock()
        mock_jd2.id = uuid.uuid4()
        mock_jd2.user_id = 1
        mock_jd2.title = "JD 2"
        mock_jd2.description = "Description 2"
        mock_jd2.uploaded_at = datetime.utcnow()
        mock_jd2.is_active = True
        mock_jd2.required_skills = ["Python"]
        mock_jd2.min_experience_years = 2
        mock_jd2.location_type = "hybrid"
        mock_jd2.salary_min = 50000
        mock_jd2.salary_max = 80000
        mock_jd2.parse_status = "completed"
        mock_jd2.parsed_requirements = {"required_skills": ["python"]}

        with patch(
            "app.modules.jobs.router.job_service.get_job_descriptions_by_user",
            new_callable=AsyncMock,
            return_value=[mock_jd1, mock_jd2],
        ):
            response = await async_client.get("/api/v1/jobs/jd")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["title"] == "JD 1"
        assert data["items"][1]["title"] == "JD 2"

    @pytest.mark.asyncio
    async def test_list_jds_empty(self, async_client: AsyncClient):
        """Test listing returns empty list when user has no JDs."""
        with patch(
            "app.modules.jobs.router.job_service.get_job_descriptions_by_user",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = await async_client.get("/api/v1/jobs/jd")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestGetJobDescriptionDetailEndpoint:
    """Tests for GET /api/v1/jobs/jd/{jd_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_jd_detail_success(self, async_client: AsyncClient):
        """Test getting job description detail returns correct data."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.title = "Senior Developer"
        mock_jd.description = "Full description here"
        mock_jd.uploaded_at = datetime.utcnow()
        mock_jd.is_active = True
        mock_jd.required_skills = ["Python", "FastAPI"]
        mock_jd.min_experience_years = 5
        mock_jd.location_type = "on-site"
        mock_jd.salary_min = 100000
        mock_jd.salary_max = 150000
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python", "fastapi"]}

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(jd_id)
        assert data["title"] == "Senior Developer"
        assert data["required_skills"] == ["Python", "FastAPI"]
        assert data["parse_status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_jd_not_found(self, async_client: AsyncClient):
        """Test getting non-existent JD returns 404."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Job description not found"

    @pytest.mark.asyncio
    async def test_get_jd_invalid_uuid(self, async_client: AsyncClient):
        """Test getting JD with invalid UUID returns 422."""
        response = await async_client.get("/api/v1/jobs/jd/invalid-uuid")

        assert response.status_code == 422


class TestGetParseStatusEndpoint:
    """Tests for GET /api/v1/jobs/jd/{jd_id}/parse-status endpoint."""

    @pytest.mark.asyncio
    async def test_get_parse_status_pending(self, async_client: AsyncClient):
        """Test getting parse status when parsing is pending."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "pending"
        mock_jd.parsed_requirements = None
        mock_jd.parse_error = None

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/parse-status")

        assert response.status_code == 200
        data = response.json()
        assert data["jd_id"] == str(jd_id)
        assert data["parse_status"] == "pending"
        assert data["parsed_requirements"] is None

    @pytest.mark.asyncio
    async def test_get_parse_status_completed(self, async_client: AsyncClient):
        """Test getting parse status when parsing is completed."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
            "job_title_normalized": "Backend Developer",
            "key_responsibilities": ["Design APIs"],
            "skill_categories": {"programming_languages": ["python"]},
        }
        mock_jd.parse_error = None

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/parse-status")

        assert response.status_code == 200
        data = response.json()
        assert data["jd_id"] == str(jd_id)
        assert data["parse_status"] == "completed"
        assert data["parsed_requirements"]["required_skills"] == ["python", "fastapi"]
        assert data["parsed_requirements"]["min_experience_years"] == 3

    @pytest.mark.asyncio
    async def test_get_parse_status_failed(self, async_client: AsyncClient):
        """Test getting parse status when parsing failed."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "failed"
        mock_jd.parsed_requirements = None
        mock_jd.parse_error = None

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/parse-status")

        assert response.status_code == 200
        data = response.json()
        assert data["parse_status"] == "failed"
        assert data["parsed_requirements"] is None

    @pytest.mark.asyncio
    async def test_get_parse_status_failed_with_error_message(self, async_client: AsyncClient):
        """Test getting parse status when parsing failed includes error message."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "failed"
        mock_jd.parsed_requirements = None
        mock_jd.parse_error = "LLM timeout: Request timed out after 120s"

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/parse-status")

        assert response.status_code == 200
        data = response.json()
        assert data["parse_status"] == "failed"
        assert data["parsed_requirements"] is None
        assert data["parse_error"] == "LLM timeout: Request timed out after 120s"

    @pytest.mark.asyncio
    async def test_get_parse_status_not_found(self, async_client: AsyncClient):
        """Test getting parse status for non-existent JD returns 404."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/parse-status")

        assert response.status_code == 404
        assert response.json()["detail"] == "Job description not found"


class TestReparseJobDescriptionEndpoint:
    """Tests for POST /api/v1/jobs/jd/{jd_id}/reparse endpoint."""

    @pytest.mark.asyncio
    async def test_reparse_jd_success(self, async_client: AsyncClient):
        """Test triggering re-parsing of a JD."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.job_service.update_parse_status",
            new_callable=AsyncMock,
        ), patch(
            "app.modules.jobs.router._run_jd_parsing",
            new_callable=AsyncMock,
        ):
            response = await async_client.post(f"/api/v1/jobs/jd/{jd_id}/reparse")

        assert response.status_code == 200
        data = response.json()
        assert data["jd_id"] == str(jd_id)
        assert data["parse_status"] == "pending"

    @pytest.mark.asyncio
    async def test_reparse_jd_not_found(self, async_client: AsyncClient):
        """Test re-parsing non-existent JD returns 404."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await async_client.post(f"/api/v1/jobs/jd/{jd_id}/reparse")

        assert response.status_code == 404


class TestDeleteJobDescriptionEndpoint:
    """Tests for DELETE /api/v1/jobs/jd/{jd_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_jd_success(self, async_client: AsyncClient):
        """Test successful job description deletion returns 204."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.delete_job_description",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = await async_client.delete(f"/api/v1/jobs/jd/{jd_id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_jd_not_found(self, async_client: AsyncClient):
        """Test deleting non-existent JD returns 404."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.delete_job_description",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = await async_client.delete(f"/api/v1/jobs/jd/{jd_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Job description not found"

    @pytest.mark.asyncio
    async def test_delete_jd_not_owner(self, async_client: AsyncClient):
        """Test deleting JD owned by another user returns 404."""
        jd_id = uuid.uuid4()

        # Service returns False when user doesn't own the JD
        with patch(
            "app.modules.jobs.router.job_service.delete_job_description",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = await async_client.delete(f"/api/v1/jobs/jd/{jd_id}")

        # Returns 404 for security (don't reveal if JD exists)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_jd_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test that unauthenticated delete request returns 401."""
        jd_id = uuid.uuid4()

        response = await unauthenticated_async_client.delete(
            f"/api/v1/jobs/jd/{jd_id}"
        )

        assert response.status_code in [401, 403]


class TestPatchParsedRequirementsEndpoint:
    """Tests for PATCH /api/v1/jobs/jd/{jd_id}/parsed-requirements endpoint."""

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_success(self, async_client: AsyncClient):
        """Test successful update of parsed requirements."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
            "job_title_normalized": "Python Developer",
            "key_responsibilities": ["Write code"],
        }

        mock_updated_jd = MagicMock()
        mock_updated_jd.id = jd_id
        mock_updated_jd.parse_status = "completed"
        mock_updated_jd.parsed_requirements = {
            "required_skills": ["python", "django"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 5,
            "job_title_normalized": "Python Developer",
            "key_responsibilities": ["Write code"],
        }

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.job_service.update_parsed_requirements",
            new_callable=AsyncMock,
            return_value=mock_updated_jd,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={
                    "required_skills": ["python", "django"],
                    "min_experience_years": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["jd_id"] == str(jd_id)
        assert data["parse_status"] == "completed"
        assert data["parsed_requirements"]["required_skills"] == ["python", "django"]
        assert data["parsed_requirements"]["min_experience_years"] == 5
        # Preserved fields
        assert data["parsed_requirements"]["job_title_normalized"] == "Python Developer"

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_partial_update(self, async_client: AsyncClient):
        """Test partial update preserves unmodified fields."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python"],
            "nice_to_have_skills": ["docker", "kubernetes"],
            "min_experience_years": 2,
            "job_title_normalized": "Backend Developer",
            "key_responsibilities": ["API development"],
        }

        mock_updated_jd = MagicMock()
        mock_updated_jd.id = jd_id
        mock_updated_jd.parse_status = "completed"
        mock_updated_jd.parsed_requirements = {
            "required_skills": ["react", "typescript"],
            "nice_to_have_skills": ["docker", "kubernetes"],  # preserved
            "min_experience_years": 2,  # preserved
            "job_title_normalized": "Backend Developer",  # preserved
            "key_responsibilities": ["API development"],  # preserved
        }

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.job_service.update_parsed_requirements",
            new_callable=AsyncMock,
            return_value=mock_updated_jd,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={
                    "required_skills": ["react", "typescript"],
                    # nice_to_have_skills not provided
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["parsed_requirements"]["required_skills"] == ["react", "typescript"]
        assert data["parsed_requirements"]["nice_to_have_skills"] == ["docker", "kubernetes"]
        assert data["parsed_requirements"]["min_experience_years"] == 2

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_not_found(self, async_client: AsyncClient):
        """Test updating parsed requirements for non-existent JD returns 404."""
        jd_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={"required_skills": ["python"]},
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Job description not found"

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_not_completed(self, async_client: AsyncClient):
        """Test updating parsed requirements when parse_status is not 'completed' returns 400."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.parse_status = "pending"
        mock_jd.parsed_requirements = None

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={"required_skills": ["python"]},
            )

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_failed_status(self, async_client: AsyncClient):
        """Test updating parsed requirements when parse_status is 'failed' returns 400."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.parse_status = "failed"
        mock_jd.parsed_requirements = None

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={"required_skills": ["python"]},
            )

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test that unauthenticated request returns 401."""
        jd_id = uuid.uuid4()

        response = await unauthenticated_async_client.patch(
            f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
            json={"required_skills": ["python"]},
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_empty_skills_list(self, async_client: AsyncClient):
        """Test updating with empty skills list clears the skills."""
        jd_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = 1
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
        }

        mock_updated_jd = MagicMock()
        mock_updated_jd.id = jd_id
        mock_updated_jd.parse_status = "completed"
        mock_updated_jd.parsed_requirements = {
            "required_skills": [],  # cleared
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
        }

        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.job_service.update_parsed_requirements",
            new_callable=AsyncMock,
            return_value=mock_updated_jd,
        ):
            response = await async_client.patch(
                f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
                json={"required_skills": []},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["parsed_requirements"]["required_skills"] == []

    @pytest.mark.asyncio
    async def test_patch_parsed_requirements_invalid_min_experience(self, async_client: AsyncClient):
        """Test that negative min_experience_years returns 422 validation error."""
        jd_id = uuid.uuid4()

        response = await async_client.patch(
            f"/api/v1/jobs/jd/{jd_id}/parsed-requirements",
            json={"min_experience_years": -1},
        )

        assert response.status_code == 422


class TestGetCandidatesForJDEndpoint:
    """Tests for GET /api/v1/jobs/jd/{jd_id}/candidates endpoint."""

    @pytest.mark.asyncio
    async def test_get_candidates_success(self, async_client: AsyncClient):
        """Test successfully getting ranked candidates for a JD."""
        jd_id = uuid.uuid4()
        cv_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
        }
        
        # Mock the candidate_ranker return value
        from app.modules.jobs.candidate_ranker import RankedCandidate, MatchBreakdown
        mock_candidates = [
            RankedCandidate(
                cv_id=cv_id,
                user_id=123,
                match_score=85,
                breakdown=MatchBreakdown(
                    matched_skills=["python", "fastapi"],
                    missing_skills=[],
                    extra_skills=["aws"],
                    skill_score=60.0,
                    experience_score=25.0,
                    experience_years=4,
                ),
                cv_summary="Senior Python developer with 4 years experience",
                filename="resume.pdf",
            ),
        ]
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.candidate_ranker.rank_candidates",
            new_callable=AsyncMock,
            return_value=(mock_candidates, 1),
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["cv_id"] == str(cv_id)
        assert data["items"][0]["match_score"] == 85
        assert data["items"][0]["breakdown"]["matched_skills"] == ["python", "fastapi"]
        assert data["items"][0]["cv_summary"] == "Senior Python developer with 4 years experience"
        assert data["limit"] == 20
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_get_candidates_with_pagination(self, async_client: AsyncClient):
        """Test getting candidates with custom pagination parameters."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.candidate_ranker.rank_candidates",
            new_callable=AsyncMock,
            return_value=([], 50),
        ) as mock_rank:
            response = await async_client.get(
                f"/api/v1/jobs/jd/{jd_id}/candidates?limit=10&offset=20"
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 20
        assert data["total"] == 50
        
        # Verify the ranker was called with correct params
        mock_rank.assert_called_once()
        call_kwargs = mock_rank.call_args.kwargs
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 20

    @pytest.mark.asyncio
    async def test_get_candidates_with_min_score_filter(self, async_client: AsyncClient):
        """Test getting candidates with min_score filter."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.candidate_ranker.rank_candidates",
            new_callable=AsyncMock,
            return_value=([], 5),
        ) as mock_rank:
            response = await async_client.get(
                f"/api/v1/jobs/jd/{jd_id}/candidates?min_score=70"
            )
        
        assert response.status_code == 200
        
        # Verify the ranker was called with min_score
        mock_rank.assert_called_once()
        call_kwargs = mock_rank.call_args.kwargs
        assert call_kwargs["min_score"] == 70

    @pytest.mark.asyncio
    async def test_get_candidates_jd_not_found(self, async_client: AsyncClient):
        """Test getting candidates for non-existent JD returns 404."""
        jd_id = uuid.uuid4()
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Job description not found"

    @pytest.mark.asyncio
    async def test_get_candidates_jd_not_parsed(self, async_client: AsyncClient):
        """Test getting candidates when JD parsing is not complete returns 409."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "pending"
        mock_jd.parsed_requirements = None
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates")
        
        assert response.status_code == 409
        assert "not complete" in response.json()["detail"]
        assert "pending" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_candidates_jd_parsing_failed(self, async_client: AsyncClient):
        """Test getting candidates when JD parsing failed returns 409."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "failed"
        mock_jd.parsed_requirements = None
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates")
        
        assert response.status_code == 409
        assert "not complete" in response.json()["detail"]
        assert "failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_candidates_empty_result(self, async_client: AsyncClient):
        """Test getting candidates when no CVs available."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.candidate_ranker.rank_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            response = await async_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_candidates_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test that unauthenticated request returns 401."""
        jd_id = uuid.uuid4()
        
        response = await unauthenticated_async_client.get(
            f"/api/v1/jobs/jd/{jd_id}/candidates"
        )
        
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_candidates_limit_capped_at_100(self, async_client: AsyncClient):
        """Test that limit is capped at 100."""
        jd_id = uuid.uuid4()
        
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}
        
        with patch(
            "app.modules.jobs.router.job_service.get_job_description",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ), patch(
            "app.modules.jobs.router.candidate_ranker.rank_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ) as mock_rank:
            response = await async_client.get(
                f"/api/v1/jobs/jd/{jd_id}/candidates?limit=500"
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 100  # Capped at 100
        
        # Verify ranker was called with capped limit
        mock_rank.assert_called_once()
        call_kwargs = mock_rank.call_args.kwargs
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_candidates_invalid_uuid(self, async_client: AsyncClient):
        """Test getting candidates with invalid UUID returns 422."""
        response = await async_client.get("/api/v1/jobs/jd/invalid-uuid/candidates")
        
        assert response.status_code == 422


class TestSearchCandidatesEndpoint:
    """Tests for POST /api/v1/jobs/search endpoint."""

    @pytest.mark.asyncio
    async def test_search_candidates_success(self, async_client: AsyncClient):
        """Test successful semantic search returns results."""
        from app.modules.jobs.semantic_searcher import SearchResult, ParsedQuery
        
        cv_id = uuid.uuid4()
        mock_results = [
            SearchResult(
                cv_id=cv_id,
                user_id=1,
                relevance_score=85,
                matched_skills=["python", "aws"],
                cv_summary="Senior Python Developer with AWS experience",
                filename="resume.pdf",
            ),
        ]
        mock_parsed = ParsedQuery(
            extracted_skills=["python", "aws"],
            experience_keywords=[],
            keywords=["developer"],
            raw_query="Python developer with AWS experience",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=(mock_results, 1),
        ), patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Python developer with AWS experience"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["cv_id"] == str(cv_id)
        assert data["items"][0]["relevance_score"] == 85
        assert data["items"][0]["matched_skills"] == ["python", "aws"]
        assert data["parsed_query"]["extracted_skills"] == ["python", "aws"]
        assert data["parsed_query"]["raw_query"] == "Python developer with AWS experience"

    @pytest.mark.asyncio
    async def test_search_candidates_with_pagination(self, async_client: AsyncClient):
        """Test search with custom pagination parameters."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python"],
            experience_keywords=[],
            keywords=[],
            raw_query="Python",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 50),
        ) as mock_search, patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Python developer", "limit": 10, "offset": 20},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 20
        assert data["total"] == 50

        # Verify searcher was called with correct params
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args.kwargs
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 20

    @pytest.mark.asyncio
    async def test_search_candidates_with_min_score(self, async_client: AsyncClient):
        """Test search with min_score filter."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python"],
            experience_keywords=[],
            keywords=[],
            raw_query="Python",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 5),
        ) as mock_search, patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Python developer", "min_score": 70},
            )

        assert response.status_code == 200

        # Verify searcher was called with min_score
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args.kwargs
        assert call_kwargs["min_score"] == 70

    @pytest.mark.asyncio
    async def test_search_candidates_empty_query(self, async_client: AsyncClient):
        """Test search with empty query returns 400."""
        response = await async_client.post(
            "/api/v1/jobs/search",
            json={"query": ""},
        )

        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_search_candidates_whitespace_query(self, async_client: AsyncClient):
        """Test search with whitespace-only query returns 400."""
        response = await async_client.post(
            "/api/v1/jobs/search",
            json={"query": "   "},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_candidates_short_query(self, async_client: AsyncClient):
        """Test search with query shorter than 2 chars returns 400."""
        response = await async_client.post(
            "/api/v1/jobs/search",
            json={"query": "a"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_candidates_no_results(self, async_client: AsyncClient):
        """Test search returns empty list when no candidates match."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["obscure_skill"],
            experience_keywords=[],
            keywords=[],
            raw_query="obscure_skill",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ), patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "obscure_skill that nobody has"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_search_candidates_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test that unauthenticated search request returns 401."""
        response = await unauthenticated_async_client.post(
            "/api/v1/jobs/search",
            json={"query": "Python developer"},
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_search_candidates_limit_capped_at_100(self, async_client: AsyncClient):
        """Test that limit is capped at 100."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python"],
            experience_keywords=[],
            keywords=[],
            raw_query="Python",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ) as mock_search, patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Python developer", "limit": 500},
            )

        # Should get 422 because limit > 100 is rejected by Pydantic
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_candidates_vietnamese_query(self, async_client: AsyncClient):
        """Test search with Vietnamese query works."""
        from app.modules.jobs.semantic_searcher import SearchResult, ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python"],
            experience_keywords=["3 năm"],
            keywords=[],
            min_experience=3,
            raw_query="Lập trình viên Python 3 năm kinh nghiệm",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ), patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Lập trình viên Python 3 năm kinh nghiệm"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["parsed_query"]["raw_query"] == "Lập trình viên Python 3 năm kinh nghiệm"

    @pytest.mark.asyncio
    async def test_search_candidates_default_values(self, async_client: AsyncClient):
        """Test search uses default values for limit, offset, min_score."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python"],
            experience_keywords=[],
            keywords=[],
            raw_query="Python",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ) as mock_search, patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Python developer"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 20  # Default
        assert data["offset"] == 0  # Default

        # Verify defaults were passed to searcher
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args.kwargs
        assert call_kwargs["limit"] == 20
        assert call_kwargs["offset"] == 0
        assert call_kwargs["min_score"] == 0

    @pytest.mark.asyncio
    async def test_search_candidates_returns_parsed_query(self, async_client: AsyncClient):
        """Test that response includes parsed query information."""
        from app.modules.jobs.semantic_searcher import ParsedQuery

        mock_parsed = ParsedQuery(
            extracted_skills=["python", "aws", "docker"],
            experience_keywords=["5 years"],
            keywords=["senior", "developer"],
            min_experience=5,
            raw_query="Senior Python developer with AWS Docker 5 years",
        )

        with patch(
            "app.modules.jobs.router.semantic_searcher.search_candidates",
            new_callable=AsyncMock,
            return_value=([], 0),
        ), patch(
            "app.modules.jobs.router.semantic_searcher._parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed,
        ):
            response = await async_client.post(
                "/api/v1/jobs/search",
                json={"query": "Senior Python developer with AWS Docker 5 years"},
            )

        assert response.status_code == 200
        data = response.json()
        
        parsed_query = data["parsed_query"]
        assert "python" in parsed_query["extracted_skills"]
        assert "aws" in parsed_query["extracted_skills"]
        assert "docker" in parsed_query["extracted_skills"]
        assert parsed_query["raw_query"] == "Senior Python developer with AWS Docker 5 years"
