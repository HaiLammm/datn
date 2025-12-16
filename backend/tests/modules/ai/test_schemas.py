"""Unit tests for AI module Pydantic schemas.

Tests for SkillBreakdown, SkillCategories, and AnalysisResult schemas.
Story 5.3: Database Schema & API Response Update
"""
import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.modules.ai.schemas import (
    SkillBreakdown,
    SkillCategories,
    AnalysisResult,
)


class TestSkillBreakdown:
    """Tests for SkillBreakdown schema."""

    def test_skill_breakdown_valid_scores(self):
        """Test valid skill breakdown with all scores in range."""
        breakdown = SkillBreakdown(
            completeness_score=5,
            categorization_score=4,
            evidence_score=3,
            market_relevance_score=4,
            total_score=16,
        )
        assert breakdown.completeness_score == 5
        assert breakdown.categorization_score == 4
        assert breakdown.evidence_score == 3
        assert breakdown.market_relevance_score == 4
        assert breakdown.total_score == 16

    def test_skill_breakdown_max_scores(self):
        """Test skill breakdown with maximum valid scores."""
        breakdown = SkillBreakdown(
            completeness_score=7,
            categorization_score=6,
            evidence_score=6,
            market_relevance_score=6,
            total_score=25,
        )
        assert breakdown.total_score == 25

    def test_skill_breakdown_min_scores(self):
        """Test skill breakdown with minimum valid scores (zeros)."""
        breakdown = SkillBreakdown(
            completeness_score=0,
            categorization_score=0,
            evidence_score=0,
            market_relevance_score=0,
            total_score=0,
        )
        assert breakdown.total_score == 0

    def test_skill_breakdown_total_matches_sum(self):
        """Test that total_score can match sum of components."""
        breakdown = SkillBreakdown(
            completeness_score=7,
            categorization_score=6,
            evidence_score=6,
            market_relevance_score=6,
            total_score=25,  # 7 + 6 + 6 + 6 = 25
        )
        expected_sum = (
            breakdown.completeness_score +
            breakdown.categorization_score +
            breakdown.evidence_score +
            breakdown.market_relevance_score
        )
        assert breakdown.total_score == expected_sum

    def test_skill_breakdown_from_dict(self):
        """Test creating SkillBreakdown from dictionary."""
        data = {
            "completeness_score": 7,
            "categorization_score": 6,
            "evidence_score": 6,
            "market_relevance_score": 6,
            "total_score": 25,
        }
        breakdown = SkillBreakdown(**data)
        assert breakdown.completeness_score == 7
        assert breakdown.total_score == 25

    def test_skill_breakdown_invalid_completeness_score_too_high(self):
        """Test that completeness_score > 7 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=10,  # max is 7
                categorization_score=4,
                evidence_score=3,
                market_relevance_score=4,
                total_score=21,
            )
        assert "completeness_score" in str(exc_info.value)

    def test_skill_breakdown_invalid_completeness_score_negative(self):
        """Test that negative completeness_score raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=-1,
                categorization_score=4,
                evidence_score=3,
                market_relevance_score=4,
                total_score=10,
            )
        assert "completeness_score" in str(exc_info.value)

    def test_skill_breakdown_invalid_categorization_score_too_high(self):
        """Test that categorization_score > 6 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=5,
                categorization_score=8,  # max is 6
                evidence_score=3,
                market_relevance_score=4,
                total_score=20,
            )
        assert "categorization_score" in str(exc_info.value)

    def test_skill_breakdown_invalid_evidence_score_too_high(self):
        """Test that evidence_score > 6 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=5,
                categorization_score=4,
                evidence_score=7,  # max is 6
                market_relevance_score=4,
                total_score=20,
            )
        assert "evidence_score" in str(exc_info.value)

    def test_skill_breakdown_invalid_market_relevance_score_too_high(self):
        """Test that market_relevance_score > 6 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=5,
                categorization_score=4,
                evidence_score=3,
                market_relevance_score=7,  # max is 6
                total_score=19,
            )
        assert "market_relevance_score" in str(exc_info.value)

    def test_skill_breakdown_invalid_total_score_too_high(self):
        """Test that total_score > 25 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SkillBreakdown(
                completeness_score=5,
                categorization_score=4,
                evidence_score=3,
                market_relevance_score=4,
                total_score=30,  # max is 25
            )
        assert "total_score" in str(exc_info.value)


class TestSkillCategories:
    """Tests for SkillCategories schema."""

    def test_skill_categories_valid(self):
        """Test valid skill categories with populated lists."""
        cats = SkillCategories(
            programming_languages=["python", "javascript"],
            frameworks=["react", "fastapi"],
            databases=["postgresql", "redis"],
            devops=["docker", "kubernetes"],
            soft_skills=["teamwork", "communication"],
            ai_ml=["machine learning", "deep learning"],
        )
        assert len(cats.programming_languages) == 2
        assert "python" in cats.programming_languages
        assert len(cats.frameworks) == 2
        assert "fastapi" in cats.frameworks

    def test_skill_categories_empty_lists(self):
        """Test that empty categories default to empty lists."""
        cats = SkillCategories()
        assert cats.programming_languages == []
        assert cats.frameworks == []
        assert cats.databases == []
        assert cats.devops == []
        assert cats.soft_skills == []
        assert cats.ai_ml == []

    def test_skill_categories_partial_init(self):
        """Test creating categories with only some fields."""
        cats = SkillCategories(
            programming_languages=["python"],
            frameworks=["django"],
        )
        assert cats.programming_languages == ["python"]
        assert cats.frameworks == ["django"]
        assert cats.databases == []
        assert cats.devops == []

    def test_skill_categories_from_dict(self):
        """Test creating SkillCategories from dictionary."""
        data = {
            "programming_languages": ["python", "go"],
            "frameworks": ["fastapi"],
            "databases": ["postgresql"],
            "devops": ["docker"],
            "soft_skills": ["leadership"],
            "ai_ml": ["nlp"],
        }
        cats = SkillCategories(**data)
        assert "python" in cats.programming_languages
        assert "go" in cats.programming_languages
        assert cats.ai_ml == ["nlp"]

    def test_skill_categories_from_dict_with_missing_keys(self):
        """Test creating SkillCategories from dict with missing keys."""
        data = {
            "programming_languages": ["rust"],
        }
        cats = SkillCategories(**data)
        assert cats.programming_languages == ["rust"]
        assert cats.frameworks == []
        assert cats.ai_ml == []


class TestAnalysisResultWithNewFields:
    """Tests for AnalysisResult with new skill fields."""

    def test_analysis_result_with_skill_breakdown(self):
        """Test AnalysisResult with skill_breakdown field."""
        breakdown = SkillBreakdown(
            completeness_score=5,
            categorization_score=4,
            evidence_score=3,
            market_relevance_score=4,
            total_score=16,
        )
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            ai_score=75,
            skill_breakdown=breakdown,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert result.skill_breakdown is not None
        assert result.skill_breakdown.completeness_score == 5
        assert result.skill_breakdown.total_score == 16

    def test_analysis_result_with_skill_categories(self):
        """Test AnalysisResult with skill_categories field."""
        categories = SkillCategories(
            programming_languages=["python", "typescript"],
            frameworks=["react", "fastapi"],
            databases=["postgresql"],
            devops=["docker"],
            soft_skills=["teamwork"],
            ai_ml=["machine learning"],
        )
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            skill_categories=categories,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert result.skill_categories is not None
        assert "python" in result.skill_categories.programming_languages

    def test_analysis_result_with_skill_recommendations(self):
        """Test AnalysisResult with skill_recommendations field."""
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            skill_recommendations=[
                "Add more cloud skills (AWS, GCP)",
                "Include DevOps certifications",
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert result.skill_recommendations is not None
        assert len(result.skill_recommendations) == 2

    def test_analysis_result_with_all_new_fields(self):
        """Test AnalysisResult with all new skill fields."""
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            ai_score=80,
            skill_breakdown=SkillBreakdown(
                completeness_score=7,
                categorization_score=6,
                evidence_score=5,
                market_relevance_score=5,
                total_score=23,
            ),
            skill_categories=SkillCategories(
                programming_languages=["python"],
                frameworks=["fastapi"],
                databases=["postgresql"],
                devops=["docker"],
                soft_skills=["leadership"],
                ai_ml=["pytorch"],
            ),
            skill_recommendations=["Add more frontend skills"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert result.skill_breakdown.total_score == 23
        assert "python" in result.skill_categories.programming_languages
        assert len(result.skill_recommendations) == 1

    def test_analysis_result_backward_compatible(self):
        """Test that old records without new fields still work."""
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            ai_score=70,
            extracted_skills=["python", "react", "postgresql"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        # Old field still works
        assert result.extracted_skills == ["python", "react", "postgresql"]
        # New fields are None
        assert result.skill_breakdown is None
        assert result.skill_categories is None
        assert result.skill_recommendations is None

    def test_analysis_result_with_both_old_and_new_fields(self):
        """Test AnalysisResult with both extracted_skills and new fields."""
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            extracted_skills=["python", "react"],  # Old field (deprecated)
            skill_categories=SkillCategories(
                programming_languages=["python"],
                frameworks=["react"],
            ),
            skill_breakdown=SkillBreakdown(
                completeness_score=5,
                categorization_score=4,
                evidence_score=4,
                market_relevance_score=4,
                total_score=17,
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        # Both old and new fields should work
        assert result.extracted_skills == ["python", "react"]
        assert result.skill_categories.programming_languages == ["python"]
        assert result.skill_breakdown.total_score == 17

    def test_analysis_result_skill_breakdown_from_dict(self):
        """Test AnalysisResult with skill_breakdown as dict (simulating DB)."""
        breakdown_dict = {
            "completeness_score": 6,
            "categorization_score": 5,
            "evidence_score": 4,
            "market_relevance_score": 5,
            "total_score": 20,
        }
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            skill_breakdown=breakdown_dict,  # type: ignore
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert result.skill_breakdown.completeness_score == 6
        assert result.skill_breakdown.total_score == 20

    def test_analysis_result_skill_categories_from_dict(self):
        """Test AnalysisResult with skill_categories as dict (simulating DB)."""
        categories_dict = {
            "programming_languages": ["java", "kotlin"],
            "frameworks": ["spring"],
            "databases": ["mysql"],
            "devops": [],
            "soft_skills": [],
            "ai_ml": [],
        }
        result = AnalysisResult(
            id=uuid.uuid4(),
            cv_id=uuid.uuid4(),
            status="COMPLETED",
            skill_categories=categories_dict,  # type: ignore
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert "java" in result.skill_categories.programming_languages
        assert result.skill_categories.frameworks == ["spring"]
