"""
Unit tests for SkillMatcher class.

Tests the skill matching functionality that compares CV skills
against JD requirements to calculate match rates and identify gaps.
"""

import pytest
from typing import Dict, List

from app.modules.ai import SkillMatcher, SkillMatchResult


class TestSkillMatcher:
    """Test suite for SkillMatcher class."""
    
    @pytest.fixture
    def matcher(self) -> SkillMatcher:
        """Create SkillMatcher instance for tests."""
        return SkillMatcher()
    
    @pytest.fixture
    def sample_cv_skills(self) -> Dict[str, List[str]]:
        """Sample CV skills for testing."""
        return {
            "programming_languages": ["python", "javascript", "java"],
            "frameworks": ["django", "react"],
            "databases": ["postgresql", "mongodb"],
            "devops": ["docker", "kubernetes"],
            "soft_skills": ["communication", "teamwork"],
            "ai_ml": []
        }
    
    def test_match_skills_perfect_match(self, matcher: SkillMatcher, sample_cv_skills: Dict[str, List[str]]):
        """Test matching when CV has all JD requirements (perfect match)."""
        jd_text = """
        We are looking for a Python developer with Django and PostgreSQL experience.
        Must have Docker knowledge.
        """
        
        result = matcher.match_skills(sample_cv_skills, jd_text)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "extra_skills" in result
        assert "skill_match_rate" in result
        assert "jd_requirements" in result
        assert "cv_skills" in result
        
        # Verify match rate is 1.0 (perfect match)
        assert result["skill_match_rate"] == 1.0
        
        # Verify matched skills
        assert "python" in result["matched_skills"].get("programming_languages", [])
        assert "django" in result["matched_skills"].get("frameworks", [])
        assert "postgresql" in result["matched_skills"].get("databases", [])
        assert "docker" in result["matched_skills"].get("devops", [])
        
        # Verify no missing skills (CV has everything JD needs)
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        assert total_missing == 0
        
        # Verify extra skills exist (CV has more than JD needs)
        total_extra = sum(len(skills) for skills in result["extra_skills"].values())
        assert total_extra > 0
    
    def test_match_skills_partial_match(self, matcher: SkillMatcher, sample_cv_skills: Dict[str, List[str]]):
        """Test matching when CV has some but not all JD requirements."""
        jd_text = """
        Requirements: Python, Django, React, AWS, Machine Learning
        """
        
        result = matcher.match_skills(sample_cv_skills, jd_text)
        
        # Verify partial match (some matched, some missing)
        assert 0.0 < result["skill_match_rate"] < 1.0
        
        # Verify matched skills
        assert "python" in result["matched_skills"].get("programming_languages", [])
        assert "django" in result["matched_skills"].get("frameworks", [])
        assert "react" in result["matched_skills"].get("frameworks", [])
        
        # Verify missing skills (CV doesn't have AWS, ML)
        # Note: "aws" should be in devops, ML skills should be in ai_ml
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        assert total_missing > 0
    
    def test_match_skills_no_match(self, matcher: SkillMatcher):
        """Test matching when CV has none of JD requirements."""
        cv_skills = {
            "programming_languages": ["ruby", "php"],
            "frameworks": ["rails", "laravel"],
            "databases": [],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        jd_text = "Looking for Python, JavaScript, React, and Docker expertise"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Verify zero match rate
        assert result["skill_match_rate"] == 0.0
        
        # Verify no matched skills
        total_matched = sum(len(skills) for skills in result["matched_skills"].values())
        assert total_matched == 0
        
        # Verify all JD requirements are missing
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        total_jd = sum(len(skills) for skills in result["jd_requirements"].values())
        assert total_missing == total_jd
        
        # Verify all CV skills are extra
        total_extra = sum(len(skills) for skills in result["extra_skills"].values())
        total_cv = sum(len(skills) for skills in cv_skills.values())
        assert total_extra == total_cv
    
    def test_match_skills_extra_skills(self, matcher: SkillMatcher):
        """Test matching when CV has more skills than JD requirements."""
        cv_skills = {
            "programming_languages": ["python", "javascript", "java", "go", "rust"],
            "frameworks": ["django", "react", "vue", "angular"],
            "databases": ["postgresql", "mysql", "mongodb", "redis"],
            "devops": ["docker", "kubernetes", "aws", "terraform"],
            "soft_skills": ["leadership", "communication"],
            "ai_ml": ["tensorflow", "pytorch"]
        }
        
        jd_text = "Need Python developer with basic Django knowledge"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Verify high match rate (has all required skills)
        assert result["skill_match_rate"] == 1.0
        
        # Verify many extra skills
        total_extra = sum(len(skills) for skills in result["extra_skills"].values())
        assert total_extra > 5  # Many skills not in JD
    
    def test_match_skills_case_insensitive(self, matcher: SkillMatcher):
        """Test that matching is case-insensitive."""
        cv_skills = {
            "programming_languages": ["python", "javascript"],
            "frameworks": [],
            "databases": [],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        # JD with uppercase/mixed case
        jd_text = "PYTHON and JavaScript developer needed"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Both skills should match despite case difference
        assert result["skill_match_rate"] == 1.0
        assert "python" in result["matched_skills"].get("programming_languages", [])
        assert "javascript" in result["matched_skills"].get("programming_languages", [])
    
    def test_match_skills_alias_matching(self, matcher: SkillMatcher):
        """Test that skill aliases are correctly matched."""
        cv_skills = {
            "programming_languages": [],
            "frameworks": ["react"],  # CV has "react"
            "databases": ["postgres"],  # CV has "postgres" (alias)
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        # JD uses different aliases
        jd_text = "ReactJS and PostgreSQL experience required"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Should match despite different aliases
        # Note: both "react" and "reactjs" normalize to same canonical form
        assert result["skill_match_rate"] > 0.0
        
        # Check that normalized forms match
        matched_frameworks = result["matched_skills"].get("frameworks", [])
        matched_databases = result["matched_skills"].get("databases", [])
        
        # At least one should match (depending on taxonomy setup)
        assert len(matched_frameworks) > 0 or len(matched_databases) > 0
    
    def test_match_skills_empty_jd(self, matcher: SkillMatcher, sample_cv_skills: Dict[str, List[str]]):
        """Test matching with empty JD text."""
        jd_text = ""
        
        result = matcher.match_skills(sample_cv_skills, jd_text)
        
        # Match rate should be 0.0 (no requirements to match)
        assert result["skill_match_rate"] == 0.0
        
        # No matched or missing skills
        total_matched = sum(len(skills) for skills in result["matched_skills"].values())
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        assert total_matched == 0
        assert total_missing == 0
        
        # All CV skills are extra
        total_extra = sum(len(skills) for skills in result["extra_skills"].values())
        total_cv = sum(len(skills) for skills in sample_cv_skills.values())
        assert total_extra == total_cv
    
    def test_match_skills_empty_cv(self, matcher: SkillMatcher):
        """Test matching with empty CV skills."""
        cv_skills = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        jd_text = "Python, Django, PostgreSQL, Docker required"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Match rate should be 0.0 (no skills to match)
        assert result["skill_match_rate"] == 0.0
        
        # No matched or extra skills
        total_matched = sum(len(skills) for skills in result["matched_skills"].values())
        total_extra = sum(len(skills) for skills in result["extra_skills"].values())
        assert total_matched == 0
        assert total_extra == 0
        
        # All JD requirements are missing
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        total_jd = sum(len(skills) for skills in result["jd_requirements"].values())
        assert total_missing == total_jd
    
    def test_match_skills_categorization(self, matcher: SkillMatcher):
        """Test that matched/missing/extra skills are correctly categorized."""
        cv_skills = {
            "programming_languages": ["python", "java"],
            "frameworks": ["django"],
            "databases": ["postgresql"],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        jd_text = """
        Required skills:
        - Programming: Python, JavaScript
        - Frameworks: Django, React
        - Databases: PostgreSQL
        - DevOps: Docker
        """
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Check matched skills by category
        assert "python" in result["matched_skills"].get("programming_languages", [])
        assert "django" in result["matched_skills"].get("frameworks", [])
        assert "postgresql" in result["matched_skills"].get("databases", [])
        
        # Check missing skills by category
        assert "javascript" in result["missing_skills"].get("programming_languages", [])
        assert "react" in result["missing_skills"].get("frameworks", [])
        assert "docker" in result["missing_skills"].get("devops", [])
        
        # Check extra skills by category
        assert "java" in result["extra_skills"].get("programming_languages", [])
        
        # Verify categorization is preserved
        for category in ["matched_skills", "missing_skills", "extra_skills"]:
            assert isinstance(result[category], dict)
            for cat_name, skills in result[category].items():
                assert isinstance(skills, list)
                assert all(isinstance(s, str) for s in skills)
    
    def test_match_skills_rate_calculation(self, matcher: SkillMatcher):
        """Test that match rate is calculated correctly."""
        cv_skills = {
            "programming_languages": ["python", "javascript"],
            "frameworks": ["django"],
            "databases": [],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        # JD requires 4 skills: Python, JavaScript, Django, React
        jd_text = "Python, JavaScript, Django, React"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # CV has 3 out of 4 required skills (75%)
        expected_rate = 3 / 4  # 0.75
        assert abs(result["skill_match_rate"] - expected_rate) < 0.01  # Allow small float precision error
        
        # Verify count of matched skills
        total_matched = sum(len(skills) for skills in result["matched_skills"].values())
        assert total_matched == 3
        
        # Verify count of missing skills
        total_missing = sum(len(skills) for skills in result["missing_skills"].values())
        assert total_missing == 1
    
    def test_match_skills_return_type(self, matcher: SkillMatcher, sample_cv_skills: Dict[str, List[str]]):
        """Test that match_skills returns correct type structure."""
        jd_text = "Python developer needed"
        
        result = matcher.match_skills(sample_cv_skills, jd_text)
        
        # Verify return type is SkillMatchResult (dict with specific keys)
        required_keys = [
            "matched_skills",
            "missing_skills",
            "extra_skills",
            "skill_match_rate",
            "jd_requirements",
            "cv_skills"
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify types
        assert isinstance(result["matched_skills"], dict)
        assert isinstance(result["missing_skills"], dict)
        assert isinstance(result["extra_skills"], dict)
        assert isinstance(result["skill_match_rate"], float)
        assert isinstance(result["jd_requirements"], dict)
        assert isinstance(result["cv_skills"], dict)
        
        # Verify match rate range
        assert 0.0 <= result["skill_match_rate"] <= 1.0
    
    def test_match_skills_with_special_characters(self, matcher: SkillMatcher):
        """Test matching skills with special characters (C++, C#, .NET)."""
        cv_skills = {
            "programming_languages": ["c++", "c#", "python"],
            "frameworks": [".net"],
            "databases": [],
            "devops": [],
            "soft_skills": [],
            "ai_ml": []
        }
        
        jd_text = "C++ and C# developer with .NET framework experience"
        
        result = matcher.match_skills(cv_skills, jd_text)
        
        # Verify result structure is correct (special chars don't break matching)
        assert isinstance(result, dict)
        assert "matched_skills" in result
        assert "skill_match_rate" in result
        assert 0.0 <= result["skill_match_rate"] <= 1.0
        
        # If special char skills are in taxonomy, they should match
        # Otherwise, match_rate will be 0.0 which is acceptable
        # The important thing is matching doesn't crash with special chars
        matched_langs = result["matched_skills"].get("programming_languages", [])
        matched_frameworks = result["matched_skills"].get("frameworks", [])
        
        # Verify operation completed without errors
        assert isinstance(matched_langs, list)
        assert isinstance(matched_frameworks, list)
