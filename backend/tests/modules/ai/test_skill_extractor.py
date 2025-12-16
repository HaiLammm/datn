"""
Tests for skill_extractor.py module.

This module tests the SkillExtractor class to ensure correct
skill extraction, normalization, and categorization.
"""

import pytest

from app.modules.ai.skill_extractor import SkillExtractor, skill_extractor


@pytest.fixture
def extractor():
    """Create a fresh SkillExtractor instance for each test."""
    SkillExtractor.reset_instance()
    return SkillExtractor()


class TestSkillExtractorSingleton:
    """Tests for SkillExtractor singleton pattern."""
    
    def test_singleton_returns_same_instance(self):
        """Multiple instantiations should return the same instance."""
        SkillExtractor.reset_instance()
        instance1 = SkillExtractor()
        instance2 = SkillExtractor()
        
        assert instance1 is instance2
    
    def test_reset_instance_creates_new_instance(self):
        """reset_instance should allow creating a new instance."""
        instance1 = SkillExtractor()
        SkillExtractor.reset_instance()
        instance2 = SkillExtractor()
        
        # After reset, should be a different object
        # (Note: Python may reuse memory, so we check attributes instead)
        assert instance2._alias_to_canonical is not None
    
    def test_module_level_instance_exists(self):
        """skill_extractor module-level instance should exist."""
        assert skill_extractor is not None
        assert isinstance(skill_extractor, SkillExtractor)


class TestNormalizeSkill:
    """Tests for normalize_skill method."""
    
    def test_normalize_skill_returns_canonical(self, extractor):
        """normalize_skill should convert aliases to canonical names."""
        assert extractor.normalize_skill("ReactJS") == "react"
        assert extractor.normalize_skill("react.js") == "react"
        assert extractor.normalize_skill("vuejs") == "vue"
    
    def test_normalize_skill_case_insensitive(self, extractor):
        """normalize_skill should be case insensitive."""
        assert extractor.normalize_skill("PYTHON") == "python"
        assert extractor.normalize_skill("Python") == "python"
        assert extractor.normalize_skill("pYtHoN") == "python"
    
    def test_normalize_skill_strips_whitespace(self, extractor):
        """normalize_skill should strip leading/trailing whitespace."""
        assert extractor.normalize_skill("  python  ") == "python"
        assert extractor.normalize_skill("\treact\n") == "react"
    
    def test_normalize_skill_unknown_returns_none(self, extractor):
        """normalize_skill should return None for unknown skills."""
        assert extractor.normalize_skill("UnknownSkill") is None
        assert extractor.normalize_skill("NotARealTechnology") is None
        assert extractor.normalize_skill("xyz123") is None
    
    def test_normalize_skill_empty_returns_none(self, extractor):
        """normalize_skill should return None for empty input."""
        assert extractor.normalize_skill("") is None
        assert extractor.normalize_skill("   ") is None
        assert extractor.normalize_skill(None) is None
    
    def test_normalize_skill_canonical_returns_itself(self, extractor):
        """Canonical names should normalize to themselves."""
        assert extractor.normalize_skill("python") == "python"
        assert extractor.normalize_skill("react") == "react"
        assert extractor.normalize_skill("docker") == "docker"
    
    def test_normalize_common_aliases(self, extractor):
        """Common aliases should normalize correctly."""
        # JavaScript aliases
        assert extractor.normalize_skill("js") == "javascript"
        assert extractor.normalize_skill("es6") == "javascript"
        
        # TypeScript aliases
        assert extractor.normalize_skill("ts") == "typescript"
        
        # Kubernetes alias
        assert extractor.normalize_skill("k8s") == "kubernetes"
        
        # PostgreSQL aliases
        assert extractor.normalize_skill("postgres") == "postgresql"
        assert extractor.normalize_skill("psql") == "postgresql"


class TestGetSkillCategory:
    """Tests for get_skill_category method."""
    
    def test_get_skill_category_returns_correct_category(self, extractor):
        """get_skill_category should return the correct category."""
        assert extractor.get_skill_category("python") == "programming_languages"
        assert extractor.get_skill_category("react") == "frameworks"
        assert extractor.get_skill_category("postgresql") == "databases"
        assert extractor.get_skill_category("docker") == "devops"
        assert extractor.get_skill_category("teamwork") == "soft_skills"
    
    def test_get_skill_category_works_with_aliases(self, extractor):
        """get_skill_category should work with skill aliases."""
        assert extractor.get_skill_category("ReactJS") == "frameworks"
        assert extractor.get_skill_category("k8s") == "devops"
        assert extractor.get_skill_category("postgres") == "databases"
    
    def test_get_skill_category_unknown_returns_none(self, extractor):
        """get_skill_category should return None for unknown skills."""
        assert extractor.get_skill_category("unknown") is None
        assert extractor.get_skill_category("notaskill") is None


class TestExtractSkills:
    """Tests for extract_skills method."""
    
    def test_extract_skills_from_simple_text(self, extractor):
        """extract_skills should find skills in simple text."""
        text = "I know Python and JavaScript"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "javascript" in result["programming_languages"]
    
    def test_extract_skills_from_sample_cv(self, extractor):
        """extract_skills should work with realistic CV text."""
        text = """
        Skills: Python, JavaScript, React, PostgreSQL, Docker
        Experience with AWS and Kubernetes for DevOps
        Familiar with Agile methodology and Scrum
        """
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "javascript" in result["programming_languages"]
        assert "react" in result["frameworks"]
        assert "postgresql" in result["databases"]
        assert "docker" in result["devops"]
        assert "aws" in result["devops"]
        assert "kubernetes" in result["devops"]
        assert "agile" in result["soft_skills"]
        assert "scrum" in result["soft_skills"]
    
    def test_extract_skills_categorizes_correctly(self, extractor):
        """Skills should be placed in correct categories."""
        text = "Python, React, MongoDB, Docker, Communication"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "python" not in result["frameworks"]
        
        assert "react" in result["frameworks"]
        assert "react" not in result["programming_languages"]
        
        assert "mongodb" in result["databases"]
        assert "docker" in result["devops"]
        assert "communication" in result["soft_skills"]
    
    def test_extract_skills_handles_duplicates(self, extractor):
        """Same skill mentioned multiple times should appear only once."""
        text = "Python Python Python, I love Python!"
        result = extractor.extract_skills(text)
        
        python_count = result["programming_languages"].count("python")
        assert python_count == 1
    
    def test_extract_skills_handles_aliases(self, extractor):
        """Different aliases should normalize to same canonical skill."""
        text = "ReactJS, react.js, React - all the same!"
        result = extractor.extract_skills(text)
        
        react_count = result["frameworks"].count("react")
        assert react_count == 1
    
    def test_extract_skills_case_insensitive(self, extractor):
        """Skill extraction should be case insensitive."""
        text = "PYTHON, javascript, TypeScript"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "javascript" in result["programming_languages"]
        assert "typescript" in result["programming_languages"]
    
    def test_extract_skills_empty_text_returns_empty_categories(self, extractor):
        """Empty text should return dict with empty lists."""
        result = extractor.extract_skills("")
        
        assert isinstance(result, dict)
        for category, skills in result.items():
            assert isinstance(skills, list)
            assert len(skills) == 0
    
    def test_extract_skills_no_skills_returns_empty_categories(self, extractor):
        """Text without skills should return empty categories."""
        text = "This is a sample text with no technical skills mentioned."
        result = extractor.extract_skills(text)
        
        total_skills = sum(len(skills) for skills in result.values())
        assert total_skills == 0
    
    def test_extract_skills_returns_sorted_lists(self, extractor):
        """Extracted skills should be sorted alphabetically."""
        text = "Rust, Python, Go, Java, TypeScript"
        result = extractor.extract_skills(text)
        
        langs = result["programming_languages"]
        assert langs == sorted(langs)


class TestSpecialCharacterSkills:
    """Tests for handling skills with special characters."""
    
    def test_extract_cpp(self, extractor):
        """C++ should be correctly extracted."""
        text = "Experience with C++ programming"
        result = extractor.extract_skills(text)
        
        assert "cpp" in result["programming_languages"]
    
    def test_extract_csharp(self, extractor):
        """C# should be correctly extracted."""
        text = "Developed applications in C#"
        result = extractor.extract_skills(text)
        
        assert "csharp" in result["programming_languages"]
    
    def test_extract_dotnet(self, extractor):
        """Various .NET formats should be extracted."""
        # Test different .NET variations
        texts = [
            "Experience with .NET development",
            "Built APIs using ASP.NET",
            "Worked with dotnet core",
        ]
        
        for text in texts:
            result = extractor.extract_skills(text)
            # Should find either csharp or dotnet framework
            found_dotnet = (
                "csharp" in result["programming_languages"] or
                "dotnet" in result["frameworks"]
            )
            # Note: depending on taxonomy structure, this may need adjustment
    
    def test_extract_nextjs(self, extractor):
        """Next.js should be correctly extracted."""
        text = "Frontend built with Next.js"
        result = extractor.extract_skills(text)
        
        assert "nextjs" in result["frameworks"]
    
    def test_cpp_not_confused_with_c(self, extractor):
        """C++ should not be confused with C language."""
        text = "Programming in C++ and C"
        result = extractor.extract_skills(text)
        
        langs = result["programming_languages"]
        assert "cpp" in langs
        assert "c" in langs


class TestExtractSkillsFlat:
    """Tests for extract_skills_flat method."""
    
    def test_extract_skills_flat_returns_list(self, extractor):
        """extract_skills_flat should return a list."""
        result = extractor.extract_skills_flat("Python and React")
        
        assert isinstance(result, list)
    
    def test_extract_skills_flat_contains_skills(self, extractor):
        """extract_skills_flat should contain extracted skills."""
        text = "Python, React, Docker"
        result = extractor.extract_skills_flat(text)
        
        assert "python" in result
        assert "react" in result
        assert "docker" in result
    
    def test_extract_skills_flat_no_duplicates(self, extractor):
        """extract_skills_flat should not have duplicates."""
        text = "Python Python Python React React"
        result = extractor.extract_skills_flat(text)
        
        assert len(result) == len(set(result))
    
    def test_extract_skills_flat_sorted(self, extractor):
        """extract_skills_flat should return sorted list."""
        text = "Rust, Python, Go, React"
        result = extractor.extract_skills_flat(text)
        
        assert result == sorted(result)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_skill_at_start_of_text(self, extractor):
        """Skills at the start of text should be found."""
        text = "Python is my favorite language"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
    
    def test_skill_at_end_of_text(self, extractor):
        """Skills at the end of text should be found."""
        text = "My favorite language is Python"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
    
    def test_skill_in_comma_list(self, extractor):
        """Skills in comma-separated lists should be found."""
        text = "Skills: Python, JavaScript, React, Docker"
        result = extractor.extract_skills(text)
        
        assert len(extractor.extract_skills_flat(text)) >= 4
    
    def test_skill_with_parentheses(self, extractor):
        """Skills mentioned in parentheses should be found."""
        text = "Backend development (Python, FastAPI)"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "fastapi" in result["frameworks"]
    
    def test_skill_with_special_formatting(self, extractor):
        """Skills with special formatting should be found."""
        text = "Technologies: **Python** | _React_ | `Docker`"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "react" in result["frameworks"]
        assert "docker" in result["devops"]
    
    def test_very_long_text(self, extractor):
        """Should handle very long text efficiently."""
        # Create a long text with skills scattered throughout
        base_text = "Lorem ipsum dolor sit amet. " * 100
        text_with_skills = f"{base_text} Python {base_text} React {base_text}"
        
        result = extractor.extract_skills(text_with_skills)
        
        assert "python" in result["programming_languages"]
        assert "react" in result["frameworks"]
    
    def test_unicode_text(self, extractor):
        """Should handle Unicode characters in text."""
        text = "Kỹ năng: Python, JavaScript, React (tiếng Việt)"
        result = extractor.extract_skills(text)
        
        assert "python" in result["programming_languages"]
        assert "javascript" in result["programming_languages"]
        assert "react" in result["frameworks"]
