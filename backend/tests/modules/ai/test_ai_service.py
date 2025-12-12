import pytest
import uuid
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.service import AIService
from app.modules.ai import models


@pytest.fixture
def ai_service():
    return AIService()


class TestAIServiceParsing:
    """Tests for AI response parsing functions."""

    def test_validate_score_valid(self, ai_service):
        """Test score validation with valid input."""
        assert ai_service._validate_score(85) == 85
        assert ai_service._validate_score("75") == 75
        assert ai_service._validate_score(0) == 0
        assert ai_service._validate_score(100) == 100

    def test_validate_score_clamping(self, ai_service):
        """Test score clamping to 0-100 range."""
        assert ai_service._validate_score(-10) == 0
        assert ai_service._validate_score(150) == 100

    def test_validate_score_invalid(self, ai_service):
        """Test score validation with invalid input returns default."""
        assert ai_service._validate_score("invalid") == 50
        assert ai_service._validate_score(None) == 50

    def test_validate_criteria_valid(self, ai_service):
        """Test criteria validation with valid input."""
        criteria = {
            "completeness": 80,
            "experience": 90,
            "skills": 85,
            "professionalism": 75
        }
        result = ai_service._validate_criteria(criteria)
        assert result["completeness"] == 80
        assert result["experience"] == 90
        assert result["skills"] == 85
        assert result["professionalism"] == 75

    def test_validate_criteria_invalid(self, ai_service):
        """Test criteria validation with invalid input returns defaults."""
        result = ai_service._validate_criteria("invalid")
        assert result["completeness"] == 50
        assert result["experience"] == 50

    def test_validate_list_valid(self, ai_service):
        """Test list validation with valid input."""
        items = ["Python", "JavaScript", "React"]
        result = ai_service._validate_list(items)
        assert result == ["Python", "JavaScript", "React"]

    def test_validate_list_invalid(self, ai_service):
        """Test list validation with invalid input returns empty list."""
        assert ai_service._validate_list("not a list") == []
        assert ai_service._validate_list(None) == []

    def test_validate_experience_valid(self, ai_service):
        """Test experience breakdown validation."""
        exp = {
            "total_years": 5,
            "key_roles": ["Software Engineer", "Tech Lead"],
            "industries": ["Technology", "Finance"]
        }
        result = ai_service._validate_experience(exp)
        assert result["total_years"] == 5
        assert "Software Engineer" in result["key_roles"]
        assert "Technology" in result["industries"]

    def test_validate_experience_invalid(self, ai_service):
        """Test experience validation with invalid input returns defaults."""
        result = ai_service._validate_experience("invalid")
        assert result["total_years"] == 0
        assert result["key_roles"] == []
        assert result["industries"] == []

    def test_parse_analysis_response_valid_json(self, ai_service):
        """Test parsing a valid AI response."""
        response = '''
        {
            "score": 85,
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 75},
            "summary": "Experienced software engineer.",
            "skills": ["Python", "React"],
            "experience_breakdown": {"total_years": 5, "key_roles": ["Engineer"], "industries": ["Tech"]},
            "strengths": ["Strong coding skills"],
            "improvements": ["Add more projects"],
            "formatting_feedback": ["Use bullet points"],
            "ats_hints": ["Include keywords"]
        }
        '''
        result = ai_service._parse_analysis_response(response)
        assert result["score"] == 85
        assert result["summary"] == "Experienced software engineer."
        assert "Python" in result["skills"]
        assert result["experience_breakdown"]["total_years"] == 5
        assert len(result["strengths"]) == 1
        assert len(result["formatting_feedback"]) == 1
        assert len(result["ats_hints"]) == 1

    def test_parse_analysis_response_malformed_json(self, ai_service):
        """Test parsing malformed JSON returns fallback values."""
        response = "This is not valid JSON"
        result = ai_service._parse_analysis_response(response)
        assert result["score"] == 50
        assert "Unable to generate" in result["summary"]

    def test_get_fallback_analysis(self, ai_service):
        """Test fallback analysis contains required fields."""
        result = ai_service._get_fallback_analysis()
        assert "score" in result
        assert "criteria" in result
        assert "summary" in result
        assert "skills" in result
        assert "experience_breakdown" in result
        assert "strengths" in result
        assert "improvements" in result
        assert "formatting_feedback" in result
        assert "ats_hints" in result


class TestAIServiceIntegration:
    """Integration tests for AI service."""

    @pytest.mark.asyncio
    async def test_analyze_cv_success(self, ai_service):
        """Test successful CV analysis with mocked Ollama calls."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"

        # Mock database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock file extraction and Ollama call
        mock_analysis_result = {
            "score": 85,
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 80},
            "summary": "Experienced software engineer with strong Python and React skills.",
            "skills": ["Python", "React", "FastAPI"],
            "experience_breakdown": {"total_years": 5, "key_roles": ["Engineer"], "industries": ["Tech"]},
            "strengths": ["Strong technical skills"],
            "improvements": ["Add certifications"],
            "formatting_feedback": ["Good structure"],
            "ats_hints": ["Include keywords"]
        }

        with patch.object(ai_service, '_extract_text_from_file', return_value="Sample CV content"):
            with patch.object(ai_service, '_perform_ai_analysis', return_value=mock_analysis_result):
                with patch.object(ai_service, '_update_analysis_status') as mock_update:
                    with patch.object(ai_service, '_save_analysis_results') as mock_save:
                        await ai_service.analyze_cv(cv_id, file_path, mock_db)

                        # Verify status updates
                        assert mock_update.call_count == 2
                        mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.PROCESSING)
                        mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.COMPLETED)

                        # Verify results saved
                        mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_cv_file_not_found(self, ai_service):
        """Test CV analysis with missing file."""
        cv_id = uuid.uuid4()
        file_path = "/nonexistent/path/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(ai_service, '_update_analysis_status') as mock_update:
            with pytest.raises(FileNotFoundError):
                await ai_service.analyze_cv(cv_id, file_path, mock_db)

            # Verify status set to FAILED
            mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.FAILED)

    @pytest.mark.asyncio
    async def test_call_ollama(self, ai_service):
        """Test Ollama API call."""
        prompt = "Test prompt"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json = Mock(return_value={"response": "Test response"})
            mock_response.raise_for_status = AsyncMock()

            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.post.return_value = mock_response

            mock_client.return_value = mock_instance

            result = await ai_service._call_ollama(prompt)

            assert result == "Test response"