"""
Tests for skill_taxonomy.py module.

This module tests the skill taxonomy structure and helper functions
to ensure they work correctly for skill extraction.
"""

import pytest

from app.modules.ai.skill_taxonomy import (
    SKILL_TAXONOMY,
    HOT_SKILLS_2024,
    get_all_skills,
    get_skill_aliases,
    get_skill_to_category,
    is_hot_skill,
)


class TestSkillTaxonomyStructure:
    """Tests for the SKILL_TAXONOMY structure."""
    
    def test_taxonomy_has_all_categories(self):
        """Verify that all required categories exist in the taxonomy."""
        required_categories = [
            "programming_languages",
            "frameworks",
            "databases",
            "devops",
            "soft_skills",
        ]
        
        for category in required_categories:
            assert category in SKILL_TAXONOMY, f"Missing category: {category}"
    
    def test_taxonomy_has_at_least_five_categories(self):
        """Taxonomy should have at least 5 main categories."""
        assert len(SKILL_TAXONOMY) >= 5
    
    def test_each_category_has_skills(self):
        """Each category should contain at least one skill."""
        for category, skills in SKILL_TAXONOMY.items():
            assert len(skills) > 0, f"Category '{category}' has no skills"
    
    def test_each_skill_has_canonical_and_aliases(self):
        """Each skill entry must have 'canonical' and 'aliases' keys."""
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                assert "canonical" in skill, \
                    f"Skill in {category} missing 'canonical' key: {skill}"
                assert "aliases" in skill, \
                    f"Skill in {category} missing 'aliases' key: {skill}"
    
    def test_canonical_names_are_lowercase(self):
        """Canonical skill names should be lowercase."""
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                canonical = skill["canonical"]
                # Allow hyphens and spaces but check for uppercase
                assert canonical == canonical.lower(), \
                    f"Canonical name not lowercase: {canonical}"
    
    def test_aliases_is_list(self):
        """Aliases should be a list (can be empty)."""
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                assert isinstance(skill["aliases"], list), \
                    f"Aliases for {skill['canonical']} is not a list"
    
    def test_no_duplicate_canonical_names(self):
        """Canonical names should be unique across all categories."""
        all_canonical = []
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                all_canonical.append(skill["canonical"])
        
        duplicates = [x for x in all_canonical if all_canonical.count(x) > 1]
        assert len(duplicates) == 0, f"Duplicate canonical names: {set(duplicates)}"


class TestHotSkills:
    """Tests for HOT_SKILLS_2024."""
    
    def test_hot_skills_has_categories(self):
        """HOT_SKILLS_2024 should have at least some categories."""
        assert len(HOT_SKILLS_2024) > 0
    
    def test_hot_skills_exist_in_taxonomy(self):
        """All hot skills should exist in the main taxonomy."""
        all_skills = get_all_skills()
        all_canonical = set()
        for skills in all_skills.values():
            all_canonical.update(skills)
        
        for category, hot_skills in HOT_SKILLS_2024.items():
            for skill in hot_skills:
                assert skill in all_canonical, \
                    f"Hot skill '{skill}' not found in taxonomy"
    
    def test_is_hot_skill_function(self):
        """is_hot_skill should correctly identify hot skills."""
        # These should be hot skills
        assert is_hot_skill("python") is True
        assert is_hot_skill("docker") is True
        assert is_hot_skill("kubernetes") is True
        
        # These should not be hot skills
        assert is_hot_skill("perl") is False
        assert is_hot_skill("cobol") is False


class TestGetAllSkills:
    """Tests for get_all_skills helper function."""
    
    def test_get_all_skills_returns_dict(self):
        """get_all_skills should return a dictionary."""
        result = get_all_skills()
        assert isinstance(result, dict)
    
    def test_get_all_skills_returns_correct_format(self):
        """get_all_skills should return Dict[str, List[str]]."""
        result = get_all_skills()
        
        for category, skills in result.items():
            assert isinstance(category, str)
            assert isinstance(skills, list)
            for skill in skills:
                assert isinstance(skill, str)
    
    def test_get_all_skills_has_all_categories(self):
        """get_all_skills should include all taxonomy categories."""
        result = get_all_skills()
        
        for category in SKILL_TAXONOMY.keys():
            assert category in result
    
    def test_get_all_skills_contains_expected_skills(self):
        """get_all_skills should contain well-known skills."""
        result = get_all_skills()
        
        assert "python" in result["programming_languages"]
        assert "react" in result["frameworks"]
        assert "postgresql" in result["databases"]
        assert "docker" in result["devops"]


class TestGetSkillAliases:
    """Tests for get_skill_aliases helper function."""
    
    def test_get_skill_aliases_returns_dict(self):
        """get_skill_aliases should return a dictionary."""
        result = get_skill_aliases()
        assert isinstance(result, dict)
    
    def test_get_skill_aliases_returns_mapping(self):
        """get_skill_aliases should map aliases to canonical names."""
        result = get_skill_aliases()
        
        # Check known aliases
        assert result.get("reactjs") == "react"
        assert result.get("react.js") == "react"
        assert result.get("js") == "javascript"
        assert result.get("ts") == "typescript"
        assert result.get("k8s") == "kubernetes"
    
    def test_canonical_maps_to_itself(self):
        """Canonical names should map to themselves."""
        result = get_skill_aliases()
        
        assert result.get("python") == "python"
        assert result.get("react") == "react"
        assert result.get("docker") == "docker"
    
    def test_all_aliases_are_lowercase(self):
        """All alias keys should be lowercase."""
        result = get_skill_aliases()
        
        for alias in result.keys():
            assert alias == alias.lower(), f"Alias not lowercase: {alias}"


class TestGetSkillToCategory:
    """Tests for get_skill_to_category helper function."""
    
    def test_get_skill_to_category_returns_dict(self):
        """get_skill_to_category should return a dictionary."""
        result = get_skill_to_category()
        assert isinstance(result, dict)
    
    def test_skill_to_category_correct_mapping(self):
        """Skills should map to correct categories."""
        result = get_skill_to_category()
        
        assert result.get("python") == "programming_languages"
        assert result.get("javascript") == "programming_languages"
        assert result.get("react") == "frameworks"
        assert result.get("django") == "frameworks"
        assert result.get("postgresql") == "databases"
        assert result.get("docker") == "devops"
        assert result.get("teamwork") == "soft_skills"


class TestSpecificSkills:
    """Tests for specific important skills in the taxonomy."""
    
    def test_programming_languages_has_common_languages(self):
        """Programming languages should include common languages."""
        skills = get_all_skills()["programming_languages"]
        
        expected = ["python", "javascript", "typescript", "java", "go", "rust"]
        for lang in expected:
            assert lang in skills, f"Missing language: {lang}"
    
    def test_frameworks_has_common_frameworks(self):
        """Frameworks should include common frameworks."""
        skills = get_all_skills()["frameworks"]
        
        expected = ["react", "vue", "angular", "django", "fastapi", "spring"]
        for fw in expected:
            assert fw in skills, f"Missing framework: {fw}"
    
    def test_databases_has_common_databases(self):
        """Databases should include common databases."""
        skills = get_all_skills()["databases"]
        
        expected = ["postgresql", "mysql", "mongodb", "redis"]
        for db in expected:
            assert db in skills, f"Missing database: {db}"
    
    def test_devops_has_common_tools(self):
        """DevOps should include common tools."""
        skills = get_all_skills()["devops"]
        
        expected = ["docker", "kubernetes", "aws", "terraform", "jenkins"]
        for tool in expected:
            assert tool in skills, f"Missing devops tool: {tool}"
    
    def test_special_character_skills_exist(self):
        """Skills with special characters should be defined."""
        aliases = get_skill_aliases()
        
        # C++ and C# should be mapped
        assert "c++" in aliases
        assert "c#" in aliases
        
        # .NET variants
        assert ".net" in aliases or "dotnet" in aliases
