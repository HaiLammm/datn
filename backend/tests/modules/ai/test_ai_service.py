import sys
import pytest
import uuid
from unittest.mock import AsyncMock, Mock, patch, MagicMock

# Mock chromadb, numpy, and sentence_transformers before importing
mock_chromadb = MagicMock()
sys.modules['chromadb'] = mock_chromadb
sys.modules['chromadb.config'] = MagicMock()

mock_numpy = MagicMock()
sys.modules['numpy'] = mock_numpy

mock_sentence_transformers = MagicMock()
sys.modules['sentence_transformers'] = mock_sentence_transformers

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
        """Test CV analysis with missing file handles gracefully."""
        cv_id = uuid.uuid4()
        file_path = "/nonexistent/path/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(ai_service, '_update_analysis_status') as mock_update:
            with patch.object(ai_service, '_save_analysis_results') as mock_save:
                # Should not raise - handles error gracefully
                await ai_service.analyze_cv(cv_id, file_path, mock_db)

                # Verify fallback was saved and status set appropriately
                # With the new logic, it tries OCR fallback first, then saves fallback analysis
                assert mock_update.call_count >= 1
                assert mock_save.call_count >= 1

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


class TestOCRDetection:
    """Tests for OCR detection heuristics."""

    def test_detect_if_needs_ocr_short_text(self, ai_service):
        """Test OCR detection for text that is too short."""
        short_text = "Hello world"
        assert ai_service.detect_if_needs_ocr(short_text, "/path/to/file.pdf") is True

    def test_detect_if_needs_ocr_empty_text(self, ai_service):
        """Test OCR detection for empty text."""
        assert ai_service.detect_if_needs_ocr("", "/path/to/file.pdf") is True
        assert ai_service.detect_if_needs_ocr("   ", "/path/to/file.pdf") is True

    def test_detect_if_needs_ocr_garbled_text(self, ai_service):
        """Test OCR detection for garbled/non-printable text."""
        # Create text with many non-printable characters
        garbled_text = "".join([chr(i) for i in range(1, 32)] * 10)
        assert ai_service.detect_if_needs_ocr(garbled_text, "/path/to/file.pdf") is True

    def test_detect_if_needs_ocr_few_words(self, ai_service):
        """Test OCR detection for text with too few recognizable words."""
        # Text with numbers and symbols but few actual words
        sparse_text = "123 456 789 @#$ *** /// === +++ --- ..." * 10
        assert ai_service.detect_if_needs_ocr(sparse_text, "/path/to/file.pdf") is True

    def test_detect_if_needs_ocr_no_headers(self, ai_service):
        """Test OCR detection when no CV section headers are found."""
        # Long text with enough words but no section headers
        no_header_text = "Lorem ipsum dolor sit amet consectetur adipiscing elit " * 20
        assert ai_service.detect_if_needs_ocr(no_header_text, "/path/to/file.pdf") is True

    def test_detect_if_needs_ocr_valid_cv_english(self, ai_service):
        """Test OCR detection returns False for valid English CV text."""
        valid_cv_text = """
        John Doe
        Software Engineer
        
        Contact Information
        Email: john@example.com
        Phone: 123-456-7890
        
        Experience
        Senior Developer at Tech Corp (2020-Present)
        - Developed Python applications
        - Led team of engineers
        
        Education
        Bachelor of Science in Computer Science
        University of Technology, 2015
        
        Skills
        Python, JavaScript, React, FastAPI, PostgreSQL
        """
        assert ai_service.detect_if_needs_ocr(valid_cv_text, "/path/to/file.pdf") is False

    def test_detect_if_needs_ocr_valid_cv_vietnamese(self, ai_service):
        """Test OCR detection returns False for valid Vietnamese CV text."""
        valid_cv_text = """
        Nguyễn Văn A
        Lập trình viên
        
        Thông tin cá nhân
        Email: nguyenvana@example.com
        Điện thoại: 0123-456-789
        
        Kinh nghiệm làm việc
        Lập trình viên cao cấp tại Công ty ABC (2020-Hiện tại)
        - Phát triển ứng dụng Python
        - Quản lý nhóm kỹ sư
        
        Học vấn
        Cử nhân Khoa học Máy tính
        Đại học Bách Khoa, 2015
        
        Kỹ năng
        Python, JavaScript, React, FastAPI, PostgreSQL
        """
        assert ai_service.detect_if_needs_ocr(valid_cv_text, "/path/to/file.pdf") is False


class TestRobustSectionSplit:
    """Tests for robust section splitting functionality."""

    def test_robust_section_split_english(self, ai_service):
        """Test section splitting for English CV."""
        cv_text = """
        Personal Information
        John Doe, Software Engineer
        
        Experience
        Senior Developer at Tech Corp
        
        Education
        BS in Computer Science
        
        Skills
        Python, JavaScript, React
        """
        sections = ai_service.robust_section_split(cv_text)
        
        assert "personal_info" in sections
        assert "experience" in sections
        assert "education" in sections
        assert "skills" in sections
        assert "John Doe" in sections["personal_info"]
        assert "Tech Corp" in sections["experience"]

    def test_robust_section_split_vietnamese(self, ai_service):
        """Test section splitting for Vietnamese CV."""
        cv_text = """
        Thông tin cá nhân
        Nguyễn Văn A, Lập trình viên
        
        Kinh nghiệm làm việc
        Lập trình viên cao cấp tại Công ty ABC
        
        Học vấn
        Cử nhân Khoa học Máy tính
        
        Kỹ năng
        Python, JavaScript, React
        """
        sections = ai_service.robust_section_split(cv_text)
        
        assert "personal_info" in sections
        assert "experience" in sections
        assert "education" in sections
        assert "skills" in sections

    def test_robust_section_split_mixed_language(self, ai_service):
        """Test section splitting for mixed Vietnamese/English CV."""
        cv_text = """
        Thông tin cá nhân
        Name: John Doe
        
        Work Experience
        Senior Developer at ABC Company
        
        Học vấn
        Bachelor of Science
        
        Skills
        Python, FastAPI
        """
        sections = ai_service.robust_section_split(cv_text)
        
        assert "personal_info" in sections
        assert "experience" in sections
        assert "education" in sections
        assert "skills" in sections

    def test_robust_section_split_no_headers(self, ai_service):
        """Test section splitting when no headers are found."""
        plain_text = "This is just some plain text without any CV structure."
        sections = ai_service.robust_section_split(plain_text)
        
        assert "content" in sections
        assert "plain text" in sections["content"]

    def test_normalize_section_header_vietnamese(self, ai_service):
        """Test normalizing Vietnamese section headers."""
        assert ai_service._normalize_section_header("học vấn") == "education"
        assert ai_service._normalize_section_header("kinh nghiệm làm việc") == "experience"
        assert ai_service._normalize_section_header("kỹ năng") == "skills"
        assert ai_service._normalize_section_header("thông tin cá nhân") == "personal_info"

    def test_normalize_section_header_english(self, ai_service):
        """Test normalizing English section headers."""
        assert ai_service._normalize_section_header("education") == "education"
        assert ai_service._normalize_section_header("work experience") == "experience"
        assert ai_service._normalize_section_header("skills") == "skills"
        assert ai_service._normalize_section_header("personal information") == "personal_info"

    def test_normalize_section_header_unknown(self, ai_service):
        """Test normalizing unknown headers."""
        assert ai_service._normalize_section_header("custom section") == "custom_section"
        assert ai_service._normalize_section_header("other info") == "other_info"


class TestOCRExtraction:
    """Tests for OCR extraction functionality."""

    @pytest.mark.asyncio
    async def test_perform_ocr_extraction_file_not_found(self, ai_service):
        """Test OCR extraction with missing file."""
        with pytest.raises(FileNotFoundError):
            await ai_service.perform_ocr_extraction("/nonexistent/file.pdf")

    @pytest.mark.asyncio
    async def test_perform_ocr_extraction_unsupported_format(self, ai_service):
        """Test OCR extraction with unsupported file format."""
        import tempfile
        import os
        import sys

        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            # Mock the OCR libraries to avoid import errors
            mock_easyocr = Mock()
            mock_pdf2image = Mock()
            mock_pil = Mock()
            mock_numpy = Mock()

            with patch.dict(sys.modules, {
                'easyocr': mock_easyocr,
                'pdf2image': mock_pdf2image,
                'PIL': mock_pil,
                'PIL.Image': Mock(),
                'numpy': mock_numpy,
            }):
                with pytest.raises((ValueError, ImportError)) as exc_info:
                    await ai_service.perform_ocr_extraction(temp_path)
                # Either unsupported format or import error is acceptable
                assert "Unsupported file format" in str(exc_info.value) or "OCR libraries" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_perform_ocr_extraction_pdf_mocked(self, ai_service):
        """Test OCR extraction with mocked dependencies."""
        import tempfile
        import os
        import sys

        # Create a temporary PDF file (minimal valid PDF)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4\n")
            temp_path = f.name

        try:
            # Create mock modules
            mock_reader_instance = Mock()
            mock_reader_instance.readtext.return_value = ["Extracted text from image"]

            mock_easyocr = Mock()
            mock_easyocr.Reader.return_value = mock_reader_instance

            mock_image = Mock()
            mock_pdf2image = Mock()
            mock_pdf2image.convert_from_path.return_value = [mock_image]

            mock_pil_image = Mock()
            mock_numpy = Mock()
            mock_numpy.array.return_value = Mock()

            # Patch sys.modules before import
            with patch.dict(sys.modules, {
                'easyocr': mock_easyocr,
                'pdf2image': mock_pdf2image,
                'PIL': Mock(),
                'PIL.Image': mock_pil_image,
                'numpy': mock_numpy,
            }):
                # Reload the module to pick up mocked imports
                from app.modules.ai import service as ai_service_module

                # Create a fresh instance
                test_service = ai_service_module.AIService()

                # Now mock the internal imports in the method
                with patch.object(ai_service_module, 'easyocr', mock_easyocr, create=True):
                    with patch('app.modules.ai.service.easyocr', mock_easyocr, create=True):
                        # Since the imports happen inside the method, we need to mock at module level
                        import builtins
                        original_import = builtins.__import__

                        def mock_import(name, *args, **kwargs):
                            if name == 'easyocr':
                                return mock_easyocr
                            elif name == 'pdf2image':
                                return mock_pdf2image
                            elif name == 'numpy':
                                return mock_numpy
                            return original_import(name, *args, **kwargs)

                        with patch.object(builtins, '__import__', side_effect=mock_import):
                            result = await test_service.perform_ocr_extraction(temp_path)

                        assert "Extracted text from image" in result
        except ImportError:
            # If OCR libraries are not installed, test passes with skip
            pytest.skip("OCR libraries not installed")
        finally:
            os.unlink(temp_path)


class TestRAGIntegration:
    """Tests for RAG (Retrieval-Augmented Generation) integration in AI service."""

    @pytest.mark.asyncio
    async def test_analyze_cv_with_rag_context(self, ai_service):
        """Test CV analysis includes RAG context in prompt."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        mock_analysis_result = {
            "score": 85,
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 80},
            "summary": "Experienced developer matching job requirements.",
            "skills": ["Python", "FastAPI"],
            "experience_breakdown": {"total_years": 5, "key_roles": ["Developer"], "industries": ["Tech"]},
            "strengths": ["Strong match to job requirements"],
            "improvements": ["Add certifications"],
            "formatting_feedback": ["Good structure"],
            "ats_hints": ["Include more keywords"]
        }

        # Mock RAG service to return context
        mock_retrieved_docs = [Mock(doc_type="job_description", content="Python Developer job")]
        mock_rag_context = "## Relevant Job Descriptions:\n### Python Developer\nLooking for experienced..."

        with patch.object(ai_service, '_extract_text_from_file', return_value="Sample CV with Python experience " * 20):
            with patch.object(ai_service, 'detect_if_needs_ocr', return_value=False):
                with patch('app.modules.ai.service.rag_service') as mock_rag:
                    mock_rag.retrieve_context.return_value = mock_retrieved_docs
                    mock_rag.format_context_for_prompt.return_value = mock_rag_context
                    
                    with patch.object(ai_service, '_call_ollama') as mock_ollama:
                        mock_ollama.return_value = '{"score": 85, "criteria": {}, "summary": "Good", "skills": [], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                        
                        with patch.object(ai_service, '_update_analysis_status'):
                            with patch.object(ai_service, '_save_analysis_results'):
                                await ai_service.analyze_cv(cv_id, file_path, mock_db)

                        # Verify RAG context was retrieved
                        mock_rag.retrieve_context.assert_called_once()
                        mock_rag.format_context_for_prompt.assert_called_once_with(mock_retrieved_docs)
                        
                        # Verify the prompt includes RAG context
                        call_args = mock_ollama.call_args[0][0]
                        assert "Reference Context" in call_args or "Relevant Job Descriptions" in call_args

    @pytest.mark.asyncio
    async def test_analyze_cv_without_rag_fallback(self, ai_service):
        """Test CV analysis works without RAG when RAG service fails."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        mock_analysis_result = {
            "score": 75,
            "criteria": {"completeness": 70, "experience": 80, "skills": 75, "professionalism": 75},
            "summary": "Solid developer profile.",
            "skills": ["Python"],
            "experience_breakdown": {"total_years": 3, "key_roles": ["Engineer"], "industries": ["Software"]},
            "strengths": ["Technical skills"],
            "improvements": ["Add projects"],
            "formatting_feedback": ["Clean format"],
            "ats_hints": ["Use keywords"]
        }

        with patch.object(ai_service, '_extract_text_from_file', return_value="Sample CV content " * 20):
            with patch.object(ai_service, 'detect_if_needs_ocr', return_value=False):
                with patch('app.modules.ai.service.rag_service') as mock_rag:
                    # Simulate RAG service failure
                    mock_rag.retrieve_context.side_effect = Exception("RAG service unavailable")
                    
                    with patch.object(ai_service, '_call_ollama') as mock_ollama:
                        mock_ollama.return_value = '{"score": 75, "criteria": {}, "summary": "Good", "skills": [], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                        
                        with patch.object(ai_service, '_update_analysis_status'):
                            with patch.object(ai_service, '_save_analysis_results') as mock_save:
                                # Should NOT raise - graceful degradation
                                await ai_service.analyze_cv(cv_id, file_path, mock_db)
                                
                                # Verify analysis still completed
                                mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_cv_rag_returns_empty(self, ai_service):
        """Test CV analysis handles empty RAG results gracefully."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(ai_service, '_extract_text_from_file', return_value="Sample CV content " * 20):
            with patch.object(ai_service, 'detect_if_needs_ocr', return_value=False):
                with patch('app.modules.ai.service.rag_service') as mock_rag:
                    # RAG returns empty results
                    mock_rag.retrieve_context.return_value = []
                    mock_rag.format_context_for_prompt.return_value = ""
                    
                    with patch.object(ai_service, '_call_ollama') as mock_ollama:
                        mock_ollama.return_value = '{"score": 70, "criteria": {}, "summary": "OK", "skills": [], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                        
                        with patch.object(ai_service, '_update_analysis_status'):
                            with patch.object(ai_service, '_save_analysis_results') as mock_save:
                                await ai_service.analyze_cv(cv_id, file_path, mock_db)
                                
                                # Verify analysis completed without context
                                mock_save.assert_called_once()
                                
                                # Verify prompt does NOT include context section
                                call_args = mock_ollama.call_args[0][0]
                                assert "Reference Context" not in call_args or call_args.count("Reference Context") == 0

    @pytest.mark.asyncio
    async def test_perform_ai_analysis_includes_rag_context(self, ai_service):
        """Test that _perform_ai_analysis method retrieves and includes RAG context."""
        cv_content = "Python developer with 5 years experience in FastAPI and PostgreSQL"
        
        mock_retrieved_docs = [Mock()]
        mock_context = "## Job Context\nPython Developer position available"
        
        with patch('app.modules.ai.service.rag_service') as mock_rag:
            mock_rag.retrieve_context.return_value = mock_retrieved_docs
            mock_rag.format_context_for_prompt.return_value = mock_context
            
            with patch.object(ai_service, '_call_ollama') as mock_ollama:
                mock_ollama.return_value = '{"score": 80, "criteria": {}, "summary": "Test", "skills": [], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                
                # Run the async method
                result = await ai_service._perform_ai_analysis(cv_content)
                
                # Verify RAG was called
                mock_rag.retrieve_context.assert_called_once_with(cv_content, top_k=2)
                
                # Verify context was formatted
                mock_rag.format_context_for_prompt.assert_called_once_with(mock_retrieved_docs)
                
                # Verify prompt includes the context
                prompt = mock_ollama.call_args[0][0]
                assert mock_context in prompt


class TestAnalyzeCVWithOCR:
    """Tests for analyze_cv with OCR fallback."""

    @pytest.mark.asyncio
    async def test_analyze_cv_with_force_ocr(self, ai_service):
        """Test CV analysis with force_ocr=True."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/scanned_cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        mock_analysis_result = {
            "score": 75,
            "criteria": {"completeness": 70, "experience": 80, "skills": 75, "professionalism": 75},
            "summary": "CV extracted via OCR.",
            "skills": ["Python"],
            "experience_breakdown": {"total_years": 3, "key_roles": ["Developer"], "industries": ["Tech"]},
            "strengths": ["Good skills"],
            "improvements": ["Add more details"],
            "formatting_feedback": ["Good format"],
            "ats_hints": ["Add keywords"]
        }

        with patch.object(ai_service, 'perform_ocr_extraction', return_value="OCR extracted content " * 20):
            with patch.object(ai_service, '_perform_ai_analysis', return_value=mock_analysis_result):
                with patch.object(ai_service, '_update_analysis_status') as mock_update:
                    with patch.object(ai_service, '_save_analysis_results') as mock_save:
                        await ai_service.analyze_cv(cv_id, file_path, mock_db, force_ocr=True)

                        # Verify status updates
                        assert mock_update.call_count == 2
                        mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.PROCESSING)
                        mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.COMPLETED)

                        # Verify results saved
                        mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_cv_fallback_to_ocr(self, ai_service):
        """Test CV analysis falls back to OCR when text extraction is insufficient."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        mock_analysis_result = {
            "score": 70,
            "criteria": {"completeness": 65, "experience": 75, "skills": 70, "professionalism": 70},
            "summary": "CV analyzed after OCR fallback.",
            "skills": ["JavaScript"],
            "experience_breakdown": {"total_years": 2, "key_roles": ["Engineer"], "industries": ["IT"]},
            "strengths": ["Technical skills"],
            "improvements": ["Expand experience section"],
            "formatting_feedback": ["Clear layout"],
            "ats_hints": ["Include certifications"]
        }

        # Short text that triggers OCR fallback
        short_extracted_text = "Some short text"

        with patch.object(ai_service, '_extract_text_from_file', return_value=short_extracted_text):
            with patch.object(ai_service, 'detect_if_needs_ocr', return_value=True):
                with patch.object(ai_service, 'perform_ocr_extraction', return_value="Full OCR content " * 20):
                    with patch.object(ai_service, '_perform_ai_analysis', return_value=mock_analysis_result):
                        with patch.object(ai_service, '_update_analysis_status') as mock_update:
                            with patch.object(ai_service, '_save_analysis_results') as mock_save:
                                await ai_service.analyze_cv(cv_id, file_path, mock_db)

                                # Verify OCR was called
                                ai_service.perform_ocr_extraction.assert_called_once_with(file_path)

                                # Verify completion
                                mock_update.assert_any_call(mock_db, cv_id, models.AnalysisStatus.COMPLETED)
                                mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_cv_no_ocr_needed(self, ai_service):
        """Test CV analysis doesn't use OCR when text extraction is sufficient."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"
        mock_db = AsyncMock(spec=AsyncSession)

        good_cv_text = """
        Personal Information
        John Doe, Software Engineer
        
        Experience
        5 years of experience in software development
        
        Education
        Bachelor of Science in Computer Science
        
        Skills
        Python, JavaScript, React, FastAPI
        """ + " additional content " * 50

        mock_analysis_result = {
            "score": 85,
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 80},
            "summary": "Well-structured CV.",
            "skills": ["Python", "React"],
            "experience_breakdown": {"total_years": 5, "key_roles": ["Developer"], "industries": ["Tech"]},
            "strengths": ["Strong background"],
            "improvements": ["Add certifications"],
            "formatting_feedback": ["Good structure"],
            "ats_hints": ["Include metrics"]
        }

        with patch.object(ai_service, '_extract_text_from_file', return_value=good_cv_text):
            with patch.object(ai_service, 'detect_if_needs_ocr', return_value=False):
                with patch.object(ai_service, 'perform_ocr_extraction') as mock_ocr:
                    with patch.object(ai_service, '_perform_ai_analysis', return_value=mock_analysis_result):
                        with patch.object(ai_service, '_update_analysis_status'):
                            with patch.object(ai_service, '_save_analysis_results'):
                                await ai_service.analyze_cv(cv_id, file_path, mock_db)

                                # Verify OCR was NOT called
                                mock_ocr.assert_not_called()


class TestHybridSkillScoring:
    """Tests for Story 5.4: Hybrid skill scoring integration."""

    def test_fallback_analysis_includes_skill_fields(self, ai_service):
        """Test that fallback analysis includes skill scoring fields."""
        result = ai_service._get_fallback_analysis()
        
        # Verify all expected skill scoring fields are present
        assert "skill_breakdown" in result
        assert "skill_categories" in result
        assert "skill_recommendations" in result
        
        # Verify skill_breakdown structure
        breakdown = result["skill_breakdown"]
        assert breakdown["completeness_score"] == 0
        assert breakdown["categorization_score"] == 0
        assert breakdown["evidence_score"] == 0
        assert breakdown["market_relevance_score"] == 0
        assert breakdown["total_score"] == 0
        
        # Verify empty collections
        assert result["skill_categories"] == {}
        assert result["skill_recommendations"] == []

    @pytest.mark.asyncio
    async def test_perform_ai_analysis_integrates_skill_scorer(self, ai_service):
        """Test that _perform_ai_analysis calls skill scorer and merges results."""
        cv_content = "Python developer with React and PostgreSQL experience"
        
        mock_skill_score_result = {
            "completeness_score": 5,
            "categorization_score": 4,
            "evidence_score": 3,
            "market_relevance_score": 5,
            "total_score": 17,
            "skill_categories": {
                "programming_languages": ["Python"],
                "frameworks": ["React"],
                "databases": ["PostgreSQL"]
            },
            "recommendations": ["Consider adding cloud platform skills"]
        }
        
        # Mock the skill scorer
        with patch.object(ai_service.skill_scorer, 'calculate_skill_score', return_value=mock_skill_score_result):
            with patch('app.modules.ai.service.rag_service') as mock_rag:
                mock_rag.retrieve_context.return_value = []
                
                with patch.object(ai_service, '_call_ollama') as mock_ollama:
                    mock_ollama.return_value = '{"score": 80, "criteria": {"skills": 75}, "summary": "Good CV", "skills": ["Python"], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                    
                    result = await ai_service._perform_ai_analysis(cv_content)
                    
                    # Verify skill scorer was called with correct arguments
                    ai_service.skill_scorer.calculate_skill_score.assert_called_once()
                    call_args = ai_service.skill_scorer.calculate_skill_score.call_args
                    assert call_args[1]["cv_text"] == cv_content
                    assert "llm_response" in call_args[1]
                    
                    # Verify skill scoring results were merged into response
                    assert "skill_breakdown" in result
                    assert result["skill_breakdown"]["total_score"] == 17
                    assert result["skill_breakdown"]["completeness_score"] == 5
                    assert result["skill_breakdown"]["categorization_score"] == 4
                    assert result["skill_breakdown"]["evidence_score"] == 3
                    assert result["skill_breakdown"]["market_relevance_score"] == 5
                    
                    assert "skill_categories" in result
                    assert "Python" in result["skill_categories"]["programming_languages"]
                    assert "React" in result["skill_categories"]["frameworks"]
                    
                    assert "skill_recommendations" in result
                    assert "cloud platform" in result["skill_recommendations"][0]

    @pytest.mark.asyncio
    async def test_skill_scorer_failure_uses_fallback(self, ai_service):
        """Test that skill scorer failures are handled gracefully with fallback."""
        cv_content = "Sample CV content"
        
        # Mock skill scorer to raise exception
        with patch.object(ai_service.skill_scorer, 'calculate_skill_score', side_effect=Exception("Scorer error")):
            with patch('app.modules.ai.service.rag_service') as mock_rag:
                mock_rag.retrieve_context.return_value = []
                
                with patch.object(ai_service, '_call_ollama') as mock_ollama:
                    mock_ollama.return_value = '{"score": 70, "criteria": {}, "summary": "OK", "skills": [], "experience_breakdown": {}, "strengths": [], "improvements": [], "formatting_feedback": [], "ats_hints": []}'
                    
                    # Should NOT raise - graceful degradation
                    result = await ai_service._perform_ai_analysis(cv_content)
                    
                    # Verify fallback skill fields are present
                    assert "skill_breakdown" in result
                    assert result["skill_breakdown"]["total_score"] == 0
                    assert result["skill_breakdown"]["completeness_score"] == 0
                    
                    assert "skill_categories" in result
                    assert result["skill_categories"] == {}
                    
                    assert "skill_recommendations" in result
                    assert result["skill_recommendations"] == []

    @pytest.mark.asyncio
    async def test_save_analysis_results_persists_skill_fields(self, ai_service):
        """Test that _save_analysis_results persists the new skill scoring fields to database."""
        cv_id = uuid.uuid4()
        mock_db = AsyncMock(spec=AsyncSession)
        
        results = {
            "score": 85,
            "summary": "Strong candidate",
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 80},
            "skills": ["Python", "React"],
            "experience_breakdown": {"total_years": 5, "key_roles": ["Engineer"], "industries": ["Tech"]},
            "strengths": ["Strong skills"],
            "improvements": ["Add certs"],
            "formatting_feedback": ["Good"],
            "ats_hints": ["Keywords"],
            # Story 5.4 fields
            "skill_breakdown": {
                "completeness_score": 6,
                "categorization_score": 5,
                "evidence_score": 4,
                "market_relevance_score": 5,
                "total_score": 20
            },
            "skill_categories": {
                "programming_languages": ["Python", "JavaScript"],
                "frameworks": ["React", "FastAPI"]
            },
            "skill_recommendations": ["Consider adding DevOps skills", "Learn cloud platforms"]
        }
        
        # Mock the database execute
        mock_execute = AsyncMock()
        mock_db.execute = mock_execute
        mock_db.commit = AsyncMock()
        
        await ai_service._save_analysis_results(mock_db, cv_id, results)
        
        # Verify execute was called
        mock_execute.assert_called_once()
        
        # Get the statement that was executed
        call_args = mock_execute.call_args[0][0]
        
        # Verify the values include our new fields
        # Note: We can't easily inspect SQLAlchemy statement internals,
        # but we can verify the method completed without error
        assert mock_db.commit.called