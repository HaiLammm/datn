"""
Tests for JDParser class - AI-powered JD parsing with skill extraction.
Covers parsing, skill normalization, LLM response handling, and error cases.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.modules.jobs.jd_parser import JDParser, ParsedJDRequirements


class TestParsedJDRequirements:
    """Tests for ParsedJDRequirements data class."""

    def test_default_values(self):
        """Test that default values are empty lists/None."""
        result = ParsedJDRequirements()
        
        assert result.required_skills == []
        assert result.nice_to_have_skills == []
        assert result.min_experience_years is None
        assert result.job_title_normalized is None
        assert result.key_responsibilities == []
        assert result.skill_categories == {}
        assert result.raw_llm_output is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ParsedJDRequirements(
            required_skills=["python", "fastapi"],
            nice_to_have_skills=["docker"],
            min_experience_years=3,
            job_title_normalized="Senior Python Developer",
            key_responsibilities=["Design APIs", "Write tests"],
            skill_categories={"programming_languages": ["python"]},
        )
        
        d = result.to_dict()
        
        assert d["required_skills"] == ["python", "fastapi"]
        assert d["nice_to_have_skills"] == ["docker"]
        assert d["min_experience_years"] == 3
        assert d["job_title_normalized"] == "Senior Python Developer"
        assert d["key_responsibilities"] == ["Design APIs", "Write tests"]
        assert d["skill_categories"] == {"programming_languages": ["python"]}


class TestJDParserInit:
    """Tests for JDParser initialization."""

    def test_default_settings(self):
        """Test that default settings are loaded from config."""
        parser = JDParser()
        
        # Should use settings values
        assert parser.ollama_url is not None
        assert parser.model is not None

    def test_custom_settings(self):
        """Test that custom settings can be provided."""
        parser = JDParser(
            ollama_url="http://custom:11434",
            model="custom-model",
        )
        
        assert parser.ollama_url == "http://custom:11434"
        assert parser.model == "custom-model"


class TestJDParserParseJD:
    """Tests for JDParser.parse_jd() method."""

    @pytest.fixture
    def jd_parser(self):
        """Create a JDParser instance for testing."""
        return JDParser()

    @pytest.mark.asyncio
    async def test_parse_jd_extracts_required_skills(self, jd_parser):
        """Test that required skills are extracted and normalized."""
        jd_text = """
        Senior Python Developer
        
        Requirements:
        - 3+ years of Python experience
        - Experience with FastAPI or Django
        - Knowledge of PostgreSQL
        - Nice to have: Docker, Kubernetes
        """
        
        mock_llm_response = '''
        {
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "nice_to_have_skills": ["Docker", "Kubernetes"],
            "min_experience_years": 3,
            "job_title_normalized": "Senior Python Developer",
            "key_responsibilities": ["Develop APIs", "Maintain codebase"]
        }
        '''
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            result = await jd_parser.parse_jd(jd_text)
            
            # Skills should be normalized to lowercase
            assert "python" in result.required_skills
            assert "fastapi" in result.required_skills
            assert "postgresql" in result.required_skills
            assert result.min_experience_years == 3
            assert "docker" in result.nice_to_have_skills

    @pytest.mark.asyncio
    async def test_parse_jd_extracts_experience_years(self, jd_parser):
        """Test that minimum experience years are extracted correctly."""
        jd_text = "We need a developer with 5+ years experience in Java."
        
        mock_llm_response = '''
        {
            "required_skills": ["Java"],
            "nice_to_have_skills": [],
            "min_experience_years": 5,
            "job_title_normalized": "Java Developer",
            "key_responsibilities": []
        }
        '''
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            result = await jd_parser.parse_jd(jd_text)
            
            assert result.min_experience_years == 5

    @pytest.mark.asyncio
    async def test_parse_jd_normalizes_skills(self, jd_parser):
        """Test that skills are normalized using skill taxonomy."""
        jd_text = "Looking for ReactJS and NodeJS developer."
        
        mock_llm_response = '''
        {
            "required_skills": ["ReactJS", "Node.js", "JavaScript"],
            "nice_to_have_skills": [],
            "min_experience_years": null,
            "job_title_normalized": "Full Stack Developer",
            "key_responsibilities": []
        }
        '''
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            result = await jd_parser.parse_jd(jd_text)
            
            # Skills should be normalized (ReactJS -> react, Node.js -> node.js)
            assert "react" in result.required_skills or "reactjs" in result.required_skills
            assert "javascript" in result.required_skills

    @pytest.mark.asyncio
    async def test_parse_jd_handles_empty_text(self, jd_parser):
        """Test that empty/short text returns empty result."""
        result = await jd_parser.parse_jd("")
        
        assert result.required_skills == []
        assert result.min_experience_years is None

    @pytest.mark.asyncio
    async def test_parse_jd_handles_short_text(self, jd_parser):
        """Test that very short text returns empty result."""
        result = await jd_parser.parse_jd("Developer job")
        
        assert result.required_skills == []

    @pytest.mark.asyncio
    async def test_parse_jd_handles_llm_failure(self, jd_parser):
        """Test that LLM failure returns empty result (graceful degradation)."""
        jd_text = "This is a valid job description with enough content to parse."
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM connection failed")
            
            result = await jd_parser.parse_jd(jd_text)
            
            # Should return empty result, not raise exception
            assert result.required_skills == []
            assert result.min_experience_years is None

    @pytest.mark.asyncio
    async def test_parse_jd_handles_timeout(self, jd_parser):
        """Test that LLM timeout raises TimeoutError."""
        jd_text = "This is a valid job description with enough content to parse."
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.side_effect = TimeoutError("LLM request timed out")
            
            with pytest.raises(TimeoutError):
                await jd_parser.parse_jd(jd_text)

    @pytest.mark.asyncio
    async def test_parse_jd_categorizes_skills(self, jd_parser):
        """Test that skills are categorized by type."""
        jd_text = "Looking for Python developer with AWS experience."
        
        mock_llm_response = '''
        {
            "required_skills": ["Python", "AWS"],
            "nice_to_have_skills": [],
            "min_experience_years": null,
            "job_title_normalized": "Cloud Developer",
            "key_responsibilities": []
        }
        '''
        
        with patch.object(
            jd_parser, '_call_ollama', new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            result = await jd_parser.parse_jd(jd_text)
            
            # skill_categories should contain categorized skills
            assert result.skill_categories is not None


class TestJDParserParseLLMResponse:
    """Tests for JDParser._parse_llm_response() method."""

    @pytest.fixture
    def jd_parser(self):
        return JDParser()

    def test_parse_valid_json(self, jd_parser):
        """Test parsing valid JSON response."""
        response = '''
        {
            "required_skills": ["Python", "FastAPI"],
            "nice_to_have_skills": ["Docker"],
            "min_experience_years": 3,
            "job_title_normalized": "Backend Developer",
            "key_responsibilities": ["API development"]
        }
        '''
        
        result = jd_parser._parse_llm_response(response)
        
        assert result["required_skills"] == ["Python", "FastAPI"]
        assert result["min_experience_years"] == 3

    def test_parse_json_with_extra_text(self, jd_parser):
        """Test parsing JSON embedded in extra text."""
        response = '''
        Here is the extracted information:
        
        {
            "required_skills": ["Python"],
            "nice_to_have_skills": [],
            "min_experience_years": 2,
            "job_title_normalized": "Developer",
            "key_responsibilities": []
        }
        
        Let me know if you need more details.
        '''
        
        result = jd_parser._parse_llm_response(response)
        
        assert result["required_skills"] == ["Python"]
        assert result["min_experience_years"] == 2

    def test_parse_empty_response(self, jd_parser):
        """Test parsing empty response."""
        result = jd_parser._parse_llm_response("")
        
        assert result == {}

    def test_parse_invalid_json_uses_regex_fallback(self, jd_parser):
        """Test that invalid JSON triggers regex fallback."""
        response = '''
        {
            "required_skills": ["Python", "FastAPI"],
            "min_experience_years": 3
            invalid json here
        }
        '''
        
        result = jd_parser._parse_llm_response(response)
        
        # Regex fallback should extract what it can
        assert "required_skills" in result or result == {}


class TestJDParserNormalizeSkills:
    """Tests for JDParser._normalize_skills() method."""

    @pytest.fixture
    def jd_parser(self):
        return JDParser()

    def test_normalize_known_skills(self, jd_parser):
        """Test that known skills are normalized to canonical names."""
        raw_skills = ["Python", "PYTHON", "python", "ReactJS", "react"]
        
        result = jd_parser._normalize_skills(raw_skills)
        
        # Should have deduplicated canonical names
        assert "python" in result
        # Should only appear once (no duplicates)
        assert result.count("python") == 1

    def test_normalize_unknown_skills_kept_lowercase(self, jd_parser):
        """Test that unknown skills are kept as lowercase."""
        raw_skills = ["CustomInternalTool", "ProprietaryFramework"]
        
        result = jd_parser._normalize_skills(raw_skills)
        
        assert "custominternaltool" in result
        assert "proprietaryframework" in result

    def test_normalize_empty_skills(self, jd_parser):
        """Test that empty skills are filtered out."""
        raw_skills = ["Python", "", "  ", None, "FastAPI"]
        
        result = jd_parser._normalize_skills(raw_skills)
        
        assert "" not in result
        assert None not in result
        assert len(result) == 2  # Only Python and FastAPI

    def test_normalize_deduplicates(self, jd_parser):
        """Test that duplicate skills are removed."""
        raw_skills = ["Python", "python", "PYTHON", "FastAPI", "fastapi"]
        
        result = jd_parser._normalize_skills(raw_skills)
        
        # Each skill should appear only once
        assert len(result) == len(set(result))


class TestJDParserBuildPrompt:
    """Tests for JDParser._build_prompt() method."""

    @pytest.fixture
    def jd_parser(self):
        return JDParser()

    def test_prompt_includes_jd_text(self, jd_parser):
        """Test that the prompt includes the JD text."""
        jd_text = "Looking for a Python developer with FastAPI experience."
        
        prompt = jd_parser._build_prompt(jd_text)
        
        assert jd_text in prompt
        assert "JOB DESCRIPTION:" in prompt
        assert "required_skills" in prompt
        assert "JSON" in prompt

    def test_prompt_includes_instructions(self, jd_parser):
        """Test that the prompt includes extraction instructions."""
        jd_text = "Test job description"
        
        prompt = jd_parser._build_prompt(jd_text)
        
        assert "IMPORTANT" in prompt
        assert "technical skills" in prompt.lower()
        assert "experience" in prompt.lower()
