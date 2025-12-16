import json
import uuid
import logging
import re
import asyncio
from typing import Dict, Any, List, Tuple
from pathlib import Path

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.core.config import settings
from . import models
from .rag_service import rag_service, RetrievedDocument

logger = logging.getLogger(__name__)

# Track number of pending Ollama requests for dynamic timeout calculation
# Base timeout per CV analysis is ~120 seconds
_BASE_TIMEOUT = 120  # seconds per CV
_pending_requests = 0
_request_lock = asyncio.Lock()

# Vietnamese and English section headers for CV parsing
SECTION_HEADERS_VI = [
    "thông tin cá nhân", "thông tin liên hệ", "giới thiệu bản thân",
    "mục tiêu nghề nghiệp", "mục tiêu", "tóm tắt",
    "học vấn", "trình độ học vấn", "bằng cấp",
    "kinh nghiệm làm việc", "kinh nghiệm", "lịch sử công việc",
    "kỹ năng", "kỹ năng chuyên môn", "năng lực",
    "chứng chỉ", "giấy chứng nhận", "bằng cấp chuyên môn",
    "dự án", "các dự án", "dự án tiêu biểu",
    "hoạt động", "hoạt động ngoại khóa", "hoạt động xã hội",
    "giải thưởng", "thành tích", "danh hiệu",
    "sở thích", "sở trường", "thông tin thêm",
    "người tham chiếu", "tham chiếu", "reference",
]

SECTION_HEADERS_EN = [
    "personal information", "contact information", "contact",
    "objective", "career objective", "summary", "professional summary",
    "education", "academic background", "qualifications",
    "experience", "work experience", "employment history", "professional experience",
    "skills", "technical skills", "core competencies", "competencies",
    "certifications", "certificates", "licenses",
    "projects", "key projects", "notable projects",
    "activities", "extracurricular activities", "volunteer work",
    "awards", "achievements", "honors",
    "interests", "hobbies", "additional information",
    "references", "referees",
]


class AIService:
    # Maximum characters for CV content to prevent timeout
    MAX_CV_CONTENT_LENGTH = 3000
    # Maximum RAG context length
    MAX_RAG_CONTEXT_LENGTH = 1000

    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL or "http://localhost:11434"
        self.model = settings.LLM_MODEL or "llama3.1:8b"

    async def analyze_cv(
        self,
        cv_id: uuid.UUID,
        file_path: str,
        db: AsyncSession,
        force_ocr: bool = False
    ) -> None:
        """
        Analyze a CV using Ollama LLM.
        Automatically detects if OCR is needed for image-based CVs.
        Updates the database with analysis results.

        Args:
            cv_id: UUID of the CV record
            file_path: Path to the CV file
            db: Database session
            force_ocr: If True, skip text extraction and go straight to OCR
        """
        try:
            # Update status to PROCESSING
            await self._update_analysis_status(db, cv_id, models.AnalysisStatus.PROCESSING)

            cv_content = ""

            if force_ocr:
                # Directly use OCR
                logger.info(f"Force OCR mode for CV: {cv_id}")
                cv_content = await self.perform_ocr_extraction(file_path)
            else:
                # Try standard text extraction first
                try:
                    cv_content = await self._extract_text_from_file(file_path)

                    # Check if we need to fall back to OCR
                    if self.detect_if_needs_ocr(cv_content, file_path):
                        logger.info(f"Falling back to OCR for CV: {cv_id}")
                        cv_content = await self.perform_ocr_extraction(file_path)

                except Exception as e:
                    # If text extraction fails, try OCR
                    logger.warning(
                        f"Text extraction failed, trying OCR: {str(e)}")
                    cv_content = await self.perform_ocr_extraction(file_path)

            if not cv_content or len(cv_content.strip()) < 50:
                raise ValueError(
                    "Could not extract sufficient text from CV file")

            # Apply robust section splitting for better analysis
            sections = self.robust_section_split(cv_content)
            logger.info(f"Extracted {len(sections)} sections from CV")

            # Perform AI analysis
            analysis_result = await self._perform_ai_analysis(cv_content)

            # Update database with results
            await self._save_analysis_results(db, cv_id, analysis_result)

            # Update status to COMPLETED
            await self._update_analysis_status(db, cv_id, models.AnalysisStatus.COMPLETED)

        except Exception as e:
            logger.error(f"CV analysis failed for cv_id={cv_id}: {str(e)}")

            # Save fallback results so user sees something useful
            try:
                fallback_result = self._get_fallback_analysis()
                fallback_result["summary"] = f"AI analysis temporarily unavailable. Error: {str(e)[
                    :100]}"
                await self._save_analysis_results(db, cv_id, fallback_result)
                # Mark as COMPLETED with fallback data instead of FAILED
                await self._update_analysis_status(db, cv_id, models.AnalysisStatus.COMPLETED)
                logger.info(f"Saved fallback analysis for cv_id={cv_id}")
            except Exception as fallback_error:
                logger.error(f"Failed to save fallback analysis: {
                             fallback_error}")
                await self._update_analysis_status(db, cv_id, models.AnalysisStatus.FAILED)

    async def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text content from PDF/DOCX file.
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"CV file not found: {file_path}")

        file_extension = path.suffix.lower()

        try:
            if file_extension == ".pdf":
                return await self._extract_text_from_pdf(file_path)
            elif file_extension in [".docx", ".doc"]:
                return await self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {str(e)}")
            raise

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF

            text_parts: List[str] = []

            with fitz.open(file_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text_parts.append(page_text)

            return "\n".join(text_parts)
        except ImportError:
            logger.error("PyMuPDF library not installed")
            raise ImportError("PyMuPDF library is required for PDF extraction")
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise

    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file using python-docx."""
        try:
            from docx import Document

            doc = Document(file_path)
            text_parts: List[str] = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip()
                                for cell in row.cells if cell.text.strip()]
                    if row_text:
                        text_parts.append(" | ".join(row_text))

            return "\n".join(text_parts)
        except ImportError:
            logger.error("python-docx library not installed")
            raise ImportError(
                "python-docx library is required for DOCX extraction")
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise

    async def _perform_ai_analysis(self, cv_content: str) -> Dict[str, Any]:
        """
        Use Ollama to analyze CV content and return structured results.
        Includes RAG context retrieval for enhanced analysis.
        Includes error handling for malformed AI responses.

        Note: Content is truncated to prevent timeout on low-resource systems.
        """
        # Truncate CV content to prevent timeout
        truncated_cv = cv_content[:self.MAX_CV_CONTENT_LENGTH]
        if len(cv_content) > self.MAX_CV_CONTENT_LENGTH:
            logger.info(f"CV content truncated from {len(cv_content)} to {
                        self.MAX_CV_CONTENT_LENGTH} chars")

        # Retrieve RAG context for enhanced analysis (with length limit)
        rag_context = ""
        try:
            retrieved_docs = rag_service.retrieve_context(
                truncated_cv, top_k=2)  # Limit results
            if retrieved_docs:
                rag_context = rag_service.format_context_for_prompt(
                    retrieved_docs)
                # Truncate RAG context if too long
                if len(rag_context) > self.MAX_RAG_CONTEXT_LENGTH:
                    rag_context = rag_context[:self.MAX_RAG_CONTEXT_LENGTH] + "..."
                    logger.info(f"RAG context truncated to {
                                self.MAX_RAG_CONTEXT_LENGTH} chars")
                logger.info(f"RAG context retrieved: {
                            len(retrieved_docs)} documents")
        except Exception as e:
            logger.warning(
                f"RAG retrieval failed, proceeding without context: {str(e)}")

        # Build context section for prompt (simplified)
        context_section = ""
        if rag_context:
            context_section = f"Reference: {rag_context}\n\n"

        # Simplified and shorter prompt for faster inference
        analysis_prompt = f"""Analyze this CV and respond with ONLY a JSON object.

{context_section}CV:
{truncated_cv}

JSON format:
{{"score":<0-100>,"criteria":{{"completeness":<0-100>,"experience":<0-100>,"skills":<0-100>,"professionalism":<0-100>}},"summary":"<brief summary>","skills":["skill1","skill2","skill3"...],"experience_breakdown":{{"total_years":<number>,"key_roles":["role1"],"industries":["industry1"]}},"strengths":["str1","str2"],"improvements":["imp1","imp2"],"formatting_feedback":["feedback1"],"ats_hints":["hint1"]}}

JSON only:"""

        try:
            result = await self._call_ollama(analysis_prompt)
            return self._parse_analysis_response(result)
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return fallback values
            return self._get_fallback_analysis()

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response with error handling for malformed JSON.
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")

            # Validate and sanitize the response
            return {
                "score": self._validate_score(data.get("score", 50)),
                "criteria": self._validate_criteria(data.get("criteria", {})),
                "summary": str(data.get("summary", "Analysis summary not available"))[:1000],
                "skills": self._validate_list(data.get("skills", []))[:50],
                "experience_breakdown": self._validate_experience(data.get("experience_breakdown", {})),
                "strengths": self._validate_list(data.get("strengths", []))[:10],
                "improvements": self._validate_list(data.get("improvements", []))[:10],
                "formatting_feedback": self._validate_list(data.get("formatting_feedback", []))[:10],
                "ats_hints": self._validate_list(data.get("ats_hints", []))[:10],
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            return self._get_fallback_analysis()

    def _validate_score(self, score: Any) -> int:
        """Validate score is between 0-100."""
        try:
            score_int = int(score)
            return max(0, min(100, score_int))
        except (TypeError, ValueError):
            return 50

    def _validate_criteria(self, criteria: Any) -> Dict[str, int]:
        """Validate criteria dictionary."""
        if not isinstance(criteria, dict):
            return {"completeness": 50, "experience": 50, "skills": 50, "professionalism": 50}

        validated = {}
        for key in ["completeness", "experience", "skills", "professionalism"]:
            validated[key] = self._validate_score(criteria.get(key, 50))
        return validated

    def _validate_list(self, items: Any) -> List[str]:
        """Validate list of strings."""
        if not isinstance(items, list):
            return []
        return [str(item)[:200] for item in items if item]

    def _validate_experience(self, exp: Any) -> Dict[str, Any]:
        """Validate experience breakdown."""
        if not isinstance(exp, dict):
            return {"total_years": 0, "key_roles": [], "industries": []}

        return {
            "total_years": self._validate_score(exp.get("total_years", 0)),
            "key_roles": self._validate_list(exp.get("key_roles", []))[:10],
            "industries": self._validate_list(exp.get("industries", []))[:10],
        }

    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when AI fails."""
        return {
            "score": 50,
            "criteria": {"completeness": 50, "experience": 50, "skills": 50, "professionalism": 50},
            "summary": "Unable to generate detailed analysis. Please try again later.",
            "skills": [],
            "experience_breakdown": {"total_years": 0, "key_roles": [], "industries": []},
            "strengths": [],
            "improvements": ["Consider using a clearer format", "Add more specific details"],
            "formatting_feedback": ["Analysis service temporarily unavailable"],
            "ats_hints": ["Use standard section headers", "Include relevant keywords"],
        }

    async def perform_ocr_extraction(self, file_path: str) -> str:
        """
        Perform OCR extraction on image-based or scanned PDF files.
        Uses EasyOCR for Vietnamese and English text recognition.

        Args:
            file_path: Path to the PDF or image file

        Returns:
            Extracted text content from OCR
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found for OCR: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            import easyocr
            from pdf2image import convert_from_path
            from PIL import Image
            import numpy as np

            # Initialize EasyOCR reader for Vietnamese and English
            reader = easyocr.Reader(['vi', 'en'], gpu=False)

            images: List[Any] = []
            file_extension = path.suffix.lower()

            if file_extension == ".pdf":
                # Convert PDF pages to images
                logger.info(f"Converting PDF to images for OCR: {file_path}")
                images = convert_from_path(file_path, dpi=300)
            elif file_extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                # Direct image file
                images = [Image.open(file_path)]
            else:
                raise ValueError(f"Unsupported file format for OCR: {
                                 file_extension}")

            extracted_texts: List[str] = []

            for i, image in enumerate(images):
                logger.info(f"Processing OCR for page {i + 1}/{len(images)}")

                # Convert PIL Image to numpy array for EasyOCR
                image_np = np.array(image)

                # Perform OCR
                results = reader.readtext(image_np, detail=0, paragraph=True)

                if results:
                    page_text = "\n".join(results)
                    extracted_texts.append(page_text)

            full_text = "\n\n".join(extracted_texts)
            logger.info(f"OCR extraction completed. Total characters: {
                        len(full_text)}")

            return full_text

        except ImportError as e:
            logger.error(f"OCR library not installed: {str(e)}")
            raise ImportError(
                "OCR libraries (easyocr, pdf2image, Pillow) are required. "
                "Please install them with: pip install easyocr pdf2image Pillow"
            )
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {str(e)}")
            raise

    def detect_if_needs_ocr(self, extracted_text: str, file_path: str) -> bool:
        """
        Determine if a file needs OCR processing based on text extraction results.

        Heuristics:
        1. Text is too short (less than 100 chars)
        2. Text contains mostly garbled/unreadable characters
        3. Text has very low ratio of recognizable words
        4. PDF has images but minimal text

        Args:
            extracted_text: Text extracted via standard method
            file_path: Path to the original file

        Returns:
            True if OCR is recommended, False otherwise
        """
        # Heuristic 1: Text too short
        if len(extracted_text.strip()) < 100:
            logger.info(f"OCR needed: Text too short ({
                        len(extracted_text)} chars)")
            return True

        # Heuristic 2: Check for garbled text (high ratio of non-printable chars)
        printable_ratio = sum(1 for c in extracted_text if c.isprintable(
        ) or c.isspace()) / len(extracted_text)
        if printable_ratio < 0.8:
            logger.info(
                f"OCR needed: Low printable ratio ({printable_ratio:.2f})")
            return True

        # Heuristic 3: Check for meaningful words
        # Split into words and check if they look like real words
        words = re.findall(r'\b[a-zA-ZÀ-ỹ]{2,}\b', extracted_text)
        if len(words) < 20:
            logger.info(
                f"OCR needed: Too few recognizable words ({len(words)})")
            return True

        # Heuristic 4: Check for common CV section headers (Vietnamese or English)
        text_lower = extracted_text.lower()
        headers_found = 0
        all_headers = SECTION_HEADERS_VI + SECTION_HEADERS_EN

        for header in all_headers:
            if header in text_lower:
                headers_found += 1

        # If we found at least one section header, text extraction likely worked
        if headers_found == 0:
            logger.info(
                "OCR needed: No section headers found in extracted text")
            return True

        logger.info(f"Standard extraction sufficient: {
                    headers_found} headers found, {len(words)} words")
        return False

    def robust_section_split(self, text: str) -> Dict[str, str]:
        """
        Split CV text into sections based on Vietnamese and English headers.

        Args:
            text: Raw CV text content

        Returns:
            Dictionary mapping section names to their content
        """
        sections: Dict[str, str] = {}

        # Combine all headers and sort by length (longest first to avoid partial matches)
        all_headers = SECTION_HEADERS_VI + SECTION_HEADERS_EN
        all_headers_sorted = sorted(all_headers, key=len, reverse=True)

        # Build regex pattern to find section headers
        # Headers are typically on their own line, possibly with punctuation
        header_pattern = r'(?:^|\n)\s*(' + '|'.join(
            re.escape(h) for h in all_headers_sorted
        ) + r')[\s:：]*(?:\n|$)'

        # Find all matches
        matches = list(re.finditer(header_pattern, text,
                       re.IGNORECASE | re.MULTILINE))

        if not matches:
            # No sections found, return entire text as "content"
            return {"content": text.strip()}

        # Extract sections based on header positions
        for i, match in enumerate(matches):
            header_name = match.group(1).strip().lower()

            # Normalize header names
            header_name = self._normalize_section_header(header_name)

            # Get content between this header and the next
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + \
                1 < len(matches) else len(text)

            content = text[start_pos:end_pos].strip()

            # Store section (merge if header already exists)
            if header_name in sections:
                sections[header_name] += "\n\n" + content
            else:
                sections[header_name] = content

        return sections

    def _normalize_section_header(self, header: str) -> str:
        """
        Normalize section header to a standard name.
        Maps Vietnamese headers to their English equivalents.
        """
        header = header.lower().strip()

        # Mapping Vietnamese to English
        header_mapping = {
            "thông tin cá nhân": "personal_info",
            "thông tin liên hệ": "contact",
            "giới thiệu bản thân": "summary",
            "mục tiêu nghề nghiệp": "objective",
            "mục tiêu": "objective",
            "tóm tắt": "summary",
            "học vấn": "education",
            "trình độ học vấn": "education",
            "bằng cấp": "education",
            "kinh nghiệm làm việc": "experience",
            "kinh nghiệm": "experience",
            "lịch sử công việc": "experience",
            "kỹ năng": "skills",
            "kỹ năng chuyên môn": "skills",
            "năng lực": "skills",
            "chứng chỉ": "certifications",
            "giấy chứng nhận": "certifications",
            "bằng cấp chuyên môn": "certifications",
            "dự án": "projects",
            "các dự án": "projects",
            "dự án tiêu biểu": "projects",
            "hoạt động": "activities",
            "hoạt động ngoại khóa": "activities",
            "hoạt động xã hội": "activities",
            "giải thưởng": "awards",
            "thành tích": "awards",
            "danh hiệu": "awards",
            "sở thích": "interests",
            "sở trường": "interests",
            "thông tin thêm": "additional",
            "người tham chiếu": "references",
            "tham chiếu": "references",
            # English mappings
            "personal information": "personal_info",
            "contact information": "contact",
            "contact": "contact",
            "objective": "objective",
            "career objective": "objective",
            "summary": "summary",
            "professional summary": "summary",
            "education": "education",
            "academic background": "education",
            "qualifications": "education",
            "experience": "experience",
            "work experience": "experience",
            "employment history": "experience",
            "professional experience": "experience",
            "skills": "skills",
            "technical skills": "skills",
            "core competencies": "skills",
            "competencies": "skills",
            "certifications": "certifications",
            "certificates": "certifications",
            "licenses": "certifications",
            "projects": "projects",
            "key projects": "projects",
            "notable projects": "projects",
            "activities": "activities",
            "extracurricular activities": "activities",
            "volunteer work": "activities",
            "awards": "awards",
            "achievements": "awards",
            "honors": "awards",
            "interests": "interests",
            "hobbies": "interests",
            "additional information": "additional",
            "references": "references",
            "referees": "references",
        }

        return header_mapping.get(header, header.replace(" ", "_"))

    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with a prompt and return the response.

        Uses dynamic timeout based on number of pending requests.
        Since Ollama processes requests sequentially, each request needs
        to wait for all pending requests to complete first.

        Timeout calculation: (pending_requests + 1) * BASE_TIMEOUT
        - 1 CV: 120s timeout
        - 2 CVs: 240s timeout (wait for 1st + process 2nd)
        - 5 CVs: 600s timeout (wait for 4 + process 5th)
        """
        global _pending_requests

        # Register this request and calculate timeout
        async with _request_lock:
            _pending_requests += 1
            queue_position = _pending_requests
            dynamic_timeout = queue_position * _BASE_TIMEOUT
            logger.info(f"Ollama request queued. Position: {
                        queue_position}, Timeout: {dynamic_timeout}s")

        try:
            async with httpx.AsyncClient(timeout=dynamic_timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Ollama analysis completed. Queue position was: {
                            queue_position}")
                return result.get("response", "")
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {dynamic_timeout}s")
            raise TimeoutError("AI service request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise
        finally:
            # Always decrement counter when done
            async with _request_lock:
                _pending_requests -= 1
                logger.info(f"Ollama request finished. Remaining in queue: {
                            _pending_requests}")

    async def _update_analysis_status(
        self,
        db: AsyncSession,
        cv_id: uuid.UUID,
        status: models.AnalysisStatus
    ) -> None:
        """
        Update the analysis status in the database.
        """
        stmt = (
            update(models.CVAnalysis)
            .where(models.CVAnalysis.cv_id == cv_id)
            .values(status=status.value)
        )
        await db.execute(stmt)
        await db.commit()

    async def _save_analysis_results(
        self,
        db: AsyncSession,
        cv_id: uuid.UUID,
        results: Dict[str, Any]
    ) -> None:
        """
        Save the AI analysis results to the database.
        """
        # Combine all feedback into ai_feedback JSON field
        feedback = {
            "criteria": results.get("criteria", {}),
            "experience_breakdown": results.get("experience_breakdown", {}),
            "strengths": results.get("strengths", []),
            "improvements": results.get("improvements", []),
            "formatting_feedback": results.get("formatting_feedback", []),
            "ats_hints": results.get("ats_hints", []),
        }

        stmt = (
            update(models.CVAnalysis)
            .where(models.CVAnalysis.cv_id == cv_id)
            .values(
                ai_score=results.get("score"),
                ai_summary=results.get("summary"),
                ai_feedback=feedback,
                extracted_skills=results.get("skills")
            )
        )
        await db.execute(stmt)
        await db.commit()


# Global AI service instance
ai_service = AIService()
