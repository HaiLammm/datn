"""
Tests for Story 9.1: Basic Job Search
Test the /api/v1/jobs/search/basic endpoint for job seekers to search jobs.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_basic_job_search_endpoint_exists(
    async_client: AsyncClient,
):
    """Test that the basic job search endpoint exists and returns 200."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={"keyword": "Python", "limit": 10, "offset": 0},
    )
    
    # Should return 200 (endpoint exists)
    assert response.status_code == 200
    data = response.json()
    
    # Should have expected response structure
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_basic_job_search_without_auth(
    unauthenticated_async_client: AsyncClient,
):
    """Test that basic job search works without authentication."""
    response = await unauthenticated_async_client.get(
        "/api/v1/jobs/search/basic",
        params={"keyword": "Developer"},
    )
    
    # Should work without auth (public endpoint)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_basic_job_search_with_location_filter(
    async_client: AsyncClient,
):
    """Test basic job search with location filter."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={"location": "remote", "limit": 10},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_basic_job_search_pagination_params(
    async_client: AsyncClient,
):
    """Test pagination parameters are accepted."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={"keyword": "Python", "limit": 5, "offset": 10},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 10


@pytest.mark.asyncio
async def test_basic_job_search_invalid_location(
    async_client: AsyncClient,
):
    """Test that invalid location type returns validation error."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={"location": "invalid_location"},
    )
    
    # Should return 422 for invalid location
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_advanced_search_params(async_client: AsyncClient):
    """Test advanced search parameters (salary, job_types)."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={
            "min_salary": 1000,
            "max_salary": 5000,
            "job_types": ["full-time", "contract"] 
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # Check if items conform to schema
    if data["items"]:
        item = data["items"][0]
        # salary_min might be None, but key should exist
        assert "salary_min" in item 
        assert "job_type" in item


@pytest.mark.asyncio
async def test_salary_validation(async_client: AsyncClient):
    """Test that max_salary < min_salary returns 422."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={
            "min_salary": 5000,
            "max_salary": 1000,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_job_type(async_client: AsyncClient):
    """Test invalid job type returns error."""
    response = await async_client.get(
        "/api/v1/jobs/search/basic",
        params={
            "job_types": ["invalid_type"]
        },
    )
    assert response.status_code == 422
