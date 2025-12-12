import json
import uuid
import logging
import re
from typing import Dict, Any, List
from pathlib import Path

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.core.config import settings
from . import models

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL or "http://localhost:11434"
        self.model = settings.LLM_MODEL or "llama3.1:8b"

    async def analyze_cv(self, cv_id: uuid.UUID, file_path: str, db: AsyncSession) -> None:
        """
        Analyze a CV using Ollama LLM.
        Updates the database with analysis results.
        """
        try:
            # Update status to PROCESSING
            await self._update_analysis_status(db, cv_id, models.AnalysisStatus.PROCESSING)

            # Extract text from PDF/DOCX file
            cv_content = await self._extract_text_from_file(file_path)

            if not cv_content or len(cv_content.strip()) < 50:
                raise ValueError("Could not extract sufficient text from CV file")

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
                fallback_result["summary"] = f"AI analysis temporarily unavailable. Error: {str(e)[:100]}"
                await self._save_analysis_results(db, cv_id, fallback_result)
                # Mark as COMPLETED with fallback data instead of FAILED
                await self._update_analysis_status(db, cv_id, models.AnalysisStatus.COMPLETED)
                logger.info(f"Saved fallback analysis for cv_id={cv_id}")
            except Exception as fallback_error:
                logger.error(f"Failed to save fallback analysis: {fallback_error}")
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
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        text_parts.append(" | ".join(row_text))

            return "\n".join(text_parts)
        except ImportError:
            logger.error("python-docx library not installed")
            raise ImportError("python-docx library is required for DOCX extraction")
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise

    async def _perform_ai_analysis(self, cv_content: str) -> Dict[str, Any]:
        """
        Use Ollama to analyze CV content and return structured results.
        Includes error handling for malformed AI responses.
        """
        # Comprehensive analysis prompt
        analysis_prompt = f"""
You are an expert CV analyzer. Analyze the following CV and provide a comprehensive assessment.

CV Content:
{cv_content}

Provide your analysis as a JSON object with the following structure:
{{
    "score": <number 0-100>,
    "criteria": {{
        "completeness": <score 0-100>,
        "experience": <score 0-100>,
        "skills": <score 0-100>,
        "professionalism": <score 0-100>
    }},
    "summary": "<2-3 sentence professional summary>",
    "skills": ["skill1", "skill2", ...],
    "experience_breakdown": {{
        "total_years": <number>,
        "key_roles": ["role1", "role2", ...],
        "industries": ["industry1", "industry2", ...]
    }},
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"],
    "formatting_feedback": ["feedback1", "feedback2", ...],
    "ats_hints": ["hint1", "hint2", ...]
}}

Return ONLY the JSON object, no additional text.
"""

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

    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with a prompt and return the response.
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
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
                return result.get("response", "")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise TimeoutError("AI service request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise

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
