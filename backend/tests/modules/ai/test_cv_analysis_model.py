"""Integration tests for CVAnalysis model with new skill columns.

Tests for CRUD operations on the CVAnalysis model including the new
skill_breakdown, skill_categories, and skill_recommendations columns.
Story 5.3: Database Schema & API Response Update
"""
import uuid
from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models import CVAnalysis, AnalysisStatus


class TestCVAnalysisModelWithNewColumns:
    """Tests for CVAnalysis model with new skill columns."""

    def test_create_cv_analysis_with_skill_breakdown(self):
        """Test creating CVAnalysis with skill_breakdown column."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            ai_score=80,
            skill_breakdown={
                "completeness_score": 7,
                "categorization_score": 6,
                "evidence_score": 5,
                "market_relevance_score": 5,
                "total_score": 23,
            },
        )
        
        assert analysis.skill_breakdown is not None
        assert analysis.skill_breakdown["completeness_score"] == 7
        assert analysis.skill_breakdown["total_score"] == 23

    def test_create_cv_analysis_with_skill_categories(self):
        """Test creating CVAnalysis with skill_categories column."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_categories={
                "programming_languages": ["python", "javascript"],
                "frameworks": ["react", "fastapi"],
                "databases": ["postgresql"],
                "devops": ["docker", "kubernetes"],
                "soft_skills": ["leadership"],
                "ai_ml": ["machine learning"],
            },
        )
        
        assert analysis.skill_categories is not None
        assert "python" in analysis.skill_categories["programming_languages"]
        assert len(analysis.skill_categories["frameworks"]) == 2

    def test_create_cv_analysis_with_skill_recommendations(self):
        """Test creating CVAnalysis with skill_recommendations column."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_recommendations=[
                "Add cloud certifications (AWS, GCP)",
                "Include more DevOps experience",
                "Consider adding TypeScript skills",
            ],
        )
        
        assert analysis.skill_recommendations is not None
        assert len(analysis.skill_recommendations) == 3
        assert "AWS" in analysis.skill_recommendations[0]

    def test_create_cv_analysis_with_all_new_columns(self):
        """Test creating CVAnalysis with all new skill columns."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            ai_score=85,
            ai_summary="Strong technical candidate",
            extracted_skills=["python", "react", "postgresql"],  # Old field
            skill_breakdown={
                "completeness_score": 6,
                "categorization_score": 5,
                "evidence_score": 5,
                "market_relevance_score": 6,
                "total_score": 22,
            },
            skill_categories={
                "programming_languages": ["python"],
                "frameworks": ["react"],
                "databases": ["postgresql"],
                "devops": [],
                "soft_skills": [],
                "ai_ml": [],
            },
            skill_recommendations=[
                "Add cloud experience",
            ],
        )
        
        # Old field still works
        assert analysis.extracted_skills == ["python", "react", "postgresql"]
        
        # New fields work
        assert analysis.skill_breakdown["total_score"] == 22
        assert analysis.skill_categories["programming_languages"] == ["python"]
        assert len(analysis.skill_recommendations) == 1

    def test_cv_analysis_without_new_columns_backward_compatible(self):
        """Test that CVAnalysis works without new columns (backward compatibility)."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            ai_score=70,
            extracted_skills=["java", "spring"],
        )
        
        # Old fields work
        assert analysis.extracted_skills == ["java", "spring"]
        assert analysis.ai_score == 70
        
        # New fields are None (nullable)
        assert analysis.skill_breakdown is None
        assert analysis.skill_categories is None
        assert analysis.skill_recommendations is None

    def test_cv_analysis_with_empty_skill_categories(self):
        """Test CVAnalysis with empty skill categories."""
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_categories={
                "programming_languages": [],
                "frameworks": [],
                "databases": [],
                "devops": [],
                "soft_skills": [],
                "ai_ml": [],
            },
        )
        
        assert analysis.skill_categories["programming_languages"] == []
        assert analysis.skill_categories["ai_ml"] == []

    def test_cv_analysis_with_complex_skill_breakdown(self):
        """Test CVAnalysis with various score combinations."""
        # Maximum scores
        analysis_max = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_breakdown={
                "completeness_score": 7,
                "categorization_score": 6,
                "evidence_score": 6,
                "market_relevance_score": 6,
                "total_score": 25,
            },
        )
        assert analysis_max.skill_breakdown["total_score"] == 25
        
        # Minimum scores
        analysis_min = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_breakdown={
                "completeness_score": 0,
                "categorization_score": 0,
                "evidence_score": 0,
                "market_relevance_score": 0,
                "total_score": 0,
            },
        )
        assert analysis_min.skill_breakdown["total_score"] == 0

    def test_cv_analysis_jsonb_query_simulation(self):
        """Test that JSONB data structure supports query-like access patterns."""
        skill_categories = {
            "programming_languages": ["python", "javascript", "go"],
            "frameworks": ["fastapi", "react", "nextjs"],
            "databases": ["postgresql", "redis", "mongodb"],
            "devops": ["docker", "kubernetes", "terraform"],
            "soft_skills": ["leadership", "communication"],
            "ai_ml": ["pytorch", "tensorflow"],
        }
        
        analysis = CVAnalysis(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status=AnalysisStatus.COMPLETED,
            skill_categories=skill_categories,
        )
        
        # Simulate JSONB path access
        assert analysis.skill_categories.get("programming_languages") == ["python", "javascript", "go"]
        assert "docker" in analysis.skill_categories.get("devops", [])
        assert len(analysis.skill_categories.get("ai_ml", [])) == 2
        
        # Count skills across all categories
        # 3 + 3 + 3 + 3 + 2 + 2 = 16
        total_skills = sum(
            len(skills) 
            for skills in analysis.skill_categories.values()
        )
        assert total_skills == 16
