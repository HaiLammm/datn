"""
RAG Service - Retrieval-Augmented Generation for CV Analysis.

This module orchestrates the RAG pipeline:
1. Index job descriptions and reference documents
2. Retrieve relevant context based on CV content
3. Format context for LLM consumption
4. Filter irrelevant context to prevent misclassification
"""

import logging
import time
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass

from app.core.config import settings
from .vector_store import vector_store
from .embeddings import embedding_service

logger = logging.getLogger(__name__)

# Additional collection for CSV job reference data
COLLECTION_JOB_REFERENCE = "job_reference_data"

# Career field keywords for relevance checking
# These help detect when RAG returns irrelevant job descriptions
CAREER_FIELD_KEYWORDS = {
    "it_software": {
        "keywords": [
            "python", "javascript", "java", "typescript", "react", "vue", "angular",
            "fastapi", "django", "flask", "node", "nodejs", "express",
            "postgresql", "mysql", "mongodb", "redis", "sql",
            "docker", "kubernetes", "aws", "azure", "gcp", "devops", "ci/cd",
            "git", "github", "gitlab", "api", "rest", "graphql",
            "developer", "engineer", "programmer", "software", "coding",
            "frontend", "backend", "fullstack", "full-stack", "web development",
            "machine learning", "ml", "ai", "data science", "algorithm",
            "microservices", "cloud", "agile", "scrum",
            # Vietnamese
            "lap trinh", "phat trien", "ky su phan mem", "lap trinh vien"
        ],
        "anti_keywords": ["trade marketing", "hygiene", "fmcg", "consumer goods", "retail promotion"]
    },
    "marketing_sales": {
        "keywords": [
            "marketing", "trade marketing", "brand", "advertising", "campaign",
            "sales", "retail", "distribution", "promotion", "fmcg",
            "consumer", "market research", "brand manager", "media",
            "digital marketing", "seo", "sem", "social media",
            # Vietnamese
            "tiep thi", "ban hang", "thuong hieu"
        ],
        "anti_keywords": ["python", "javascript", "react", "postgresql", "docker", "kubernetes"]
    },
    "finance_accounting": {
        "keywords": [
            "finance", "accounting", "audit", "tax", "budget", "financial",
            "investment", "banking", "loan", "credit", "treasury",
            # Vietnamese
            "tai chinh", "ke toan", "kiem toan"
        ],
        "anti_keywords": []
    }
}


@dataclass
class RetrievedDocument:
    """Represents a document retrieved from the vector store."""
    id: str
    content: str
    doc_type: str  # "job_description" or "reference"
    score: float
    metadata: Dict[str, Any]


class RAGService:
    """
    Service for Retrieval-Augmented Generation in CV analysis.
    
    Provides methods to:
    - Index job descriptions for semantic retrieval
    - Load and index reference documents (scoring criteria, guidelines)
    - Retrieve relevant context for CV analysis
    - Filter irrelevant context to prevent misclassification
    - Format context for LLM prompts
    """
    
    _instance: Optional["RAGService"] = None
    _reference_docs_loaded: bool = False
    
    def __new__(cls) -> "RAGService":
        """Singleton pattern for RAG service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the RAG service."""
        self._jobs_collection = settings.CHROMA_COLLECTION_JOBS
        self._reference_collection = settings.CHROMA_COLLECTION_REFERENCE
        self._top_k = settings.RAG_TOP_K
        self._min_similarity_score = settings.RAG_MIN_SIMILARITY_SCORE
        self._relevance_check_enabled = settings.RAG_RELEVANCE_CHECK_ENABLED
    
    @property
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return vector_store.is_available and embedding_service.is_available
    
    def detect_career_field(self, text: str) -> Tuple[str, float]:
        """
        Detect the primary career field from text content.
        
        Args:
            text: The text content (CV or job description)
            
        Returns:
            Tuple of (career_field, confidence_score)
            career_field is one of: "it_software", "marketing_sales", "finance_accounting", "unknown"
        """
        text_lower = text.lower()
        
        scores = {}
        for field, config in CAREER_FIELD_KEYWORDS.items():
            # Count keyword matches
            keyword_matches = sum(1 for kw in config["keywords"] if kw in text_lower)
            anti_matches = sum(1 for kw in config["anti_keywords"] if kw in text_lower)
            
            # Calculate score: positive for matches, negative for anti-matches
            score = keyword_matches - (anti_matches * 2)  # Anti-matches have higher weight
            scores[field] = score
        
        if not scores or max(scores.values()) <= 0:
            return ("unknown", 0.0)
        
        # Find the field with highest score
        best_field = max(scores, key=scores.get)
        best_score = scores[best_field]
        
        # Calculate confidence (normalize to 0-1 range)
        total_keywords = len(CAREER_FIELD_KEYWORDS[best_field]["keywords"])
        confidence = min(1.0, best_score / max(total_keywords * 0.3, 1))
        
        return (best_field, confidence)
    
    def is_context_relevant(
        self,
        cv_career_field: str,
        context_content: str,
        similarity_score: float
    ) -> bool:
        """
        Check if retrieved context is relevant to the CV's career field.
        
        This prevents marketing job descriptions from being used as context
        for IT professional CVs, which causes misclassification.
        
        Args:
            cv_career_field: The detected career field of the CV
            context_content: The content of the retrieved context
            similarity_score: The semantic similarity score
            
        Returns:
            True if context is relevant, False otherwise
        """
        # Always filter by minimum similarity score
        if similarity_score < self._min_similarity_score:
            logger.debug(f"Context filtered: score {similarity_score:.2f} < threshold {self._min_similarity_score}")
            return False
        
        if not self._relevance_check_enabled:
            return True
        
        if cv_career_field == "unknown":
            # Can't determine relevance, allow all
            return True
        
        # Detect career field of the context
        context_field, context_confidence = self.detect_career_field(context_content)
        
        if context_field == "unknown":
            # Can't determine context field, allow it
            return True
        
        # Check for career field mismatch
        if cv_career_field != context_field and context_confidence > 0.3:
            # Check for anti-keywords in context
            cv_config = CAREER_FIELD_KEYWORDS.get(cv_career_field, {})
            anti_keywords = cv_config.get("anti_keywords", [])
            
            context_lower = context_content.lower()
            found_anti = [kw for kw in anti_keywords if kw in context_lower]
            
            if found_anti:
                logger.warning(
                    f"Context filtered: CV field '{cv_career_field}' but context contains "
                    f"anti-keywords: {found_anti[:3]}. Score: {similarity_score:.2f}"
                )
                return False
        
        return True
    
    def index_job_description(
        self,
        jd_id: str,
        title: str,
        description: str,
        required_skills: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Index a job description for semantic retrieval.
        
        Args:
            jd_id: Unique identifier for the job description
            title: Job title
            description: Full job description text
            required_skills: List of required skills
            user_id: Owner user ID for filtering
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("RAG service not available, skipping JD indexing")
            return False
        
        try:
            # Combine title and description for embedding
            content = f"Job Title: {title}\n\nDescription: {description}"
            if required_skills:
                content += f"\n\nRequired Skills: {', '.join(required_skills)}"
            
            # Generate embedding
            embedding = embedding_service.generate_embedding(content)
            if embedding is None:
                logger.error(f"Failed to generate embedding for JD {jd_id}")
                return False
            
            # Prepare metadata
            metadata = {
                "title": title[:200],  # Truncate for ChromaDB metadata limits
                "user_id": str(user_id) if user_id else "",
                "doc_type": "job_description"
            }
            if required_skills:
                metadata["skills"] = ", ".join(required_skills[:10])  # Limit skills
            
            # Index in vector store
            success = vector_store.index_document(
                collection_name=self._jobs_collection,
                doc_id=jd_id,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Indexed job description: {jd_id} - {title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index job description {jd_id}: {str(e)}")
            return False
    
    def delete_job_description(self, jd_id: str) -> bool:
        """Delete a job description from the index."""
        return vector_store.delete_document(self._jobs_collection, jd_id)
    
    def load_reference_documents(self, force_reload: bool = False) -> bool:
        """
        Load and index reference documents from the filesystem.
        
        Args:
            force_reload: If True, reload even if already loaded
            
        Returns:
            True if successful, False otherwise
        """
        if self._reference_docs_loaded and not force_reload:
            logger.debug("Reference documents already loaded")
            return True
        
        if not self.is_available:
            logger.warning("RAG service not available, skipping reference docs loading")
            return False
        
        try:
            # Find reference documents
            reference_path = Path("data/rag_reference")
            if not reference_path.exists():
                logger.warning(f"Reference path does not exist: {reference_path}")
                return False
            
            doc_files = list(reference_path.glob("*.txt"))
            if not doc_files:
                logger.warning("No reference documents found")
                return False
            
            logger.info(f"Loading {len(doc_files)} reference documents")
            
            doc_ids = []
            contents = []
            metadatas = []
            
            for doc_file in doc_files:
                try:
                    content = doc_file.read_text(encoding="utf-8")
                    doc_id = f"ref_{doc_file.stem}"
                    
                    # Determine language from filename
                    lang = "vi" if "_vi" in doc_file.stem else "en"
                    
                    doc_ids.append(doc_id)
                    contents.append(content)
                    metadatas.append({
                        "filename": doc_file.name,
                        "doc_type": "reference",
                        "language": lang
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to read {doc_file}: {str(e)}")
            
            if not doc_ids:
                return False
            
            # Generate embeddings in batch
            embeddings = embedding_service.generate_embeddings_batch(contents)
            
            # Filter out failed embeddings
            valid_data = [
                (doc_ids[i], contents[i], embeddings[i], metadatas[i])
                for i in range(len(doc_ids))
                if embeddings[i] is not None
            ]
            
            if not valid_data:
                logger.error("All reference document embeddings failed")
                return False
            
            # Index in batch
            success = vector_store.index_documents_batch(
                collection_name=self._reference_collection,
                doc_ids=[d[0] for d in valid_data],
                contents=[d[1] for d in valid_data],
                embeddings=[d[2] for d in valid_data],
                metadatas=[d[3] for d in valid_data]
            )
            
            if success:
                self._reference_docs_loaded = True
                logger.info(f"Loaded {len(valid_data)} reference documents")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to load reference documents: {str(e)}")
            return False
    
    def retrieve_context(
        self,
        cv_content: str,
        top_k: Optional[int] = None,
        user_id: Optional[int] = None,
        include_jobs: bool = True,
        include_reference: bool = True,
        include_job_reference: bool = True
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant context for CV analysis.
        
        Args:
            cv_content: The CV text content to find context for
            top_k: Number of results per collection (default from settings)
            user_id: Filter job descriptions by user ID
            include_jobs: Whether to include job descriptions
            include_reference: Whether to include reference documents
            include_job_reference: Whether to include CSV job reference data
            
        Returns:
            List of retrieved documents sorted by relevance, filtered for career field match
        """
        if not self.is_available:
            logger.warning("RAG service not available, returning empty context")
            return []
        
        start_time = time.time()
        top_k = top_k or self._top_k
        results: List[RetrievedDocument] = []
        
        # Detect CV career field for relevance filtering
        cv_career_field, cv_confidence = self.detect_career_field(cv_content)
        logger.info(f"Detected CV career field: {cv_career_field} (confidence: {cv_confidence:.2f})")
        
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(cv_content)
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []
            
            # Query job descriptions
            if include_jobs:
                try:
                    where_filter = None
                    if user_id:
                        where_filter = {"user_id": str(user_id)}
                    
                    job_results = vector_store.query_similar(
                        collection_name=self._jobs_collection,
                        query_embedding=query_embedding,
                        top_k=top_k * 2,  # Fetch more to allow for filtering
                        where_filter=where_filter
                    )
                    
                    for doc in job_results:
                        # Apply relevance filtering
                        if self.is_context_relevant(cv_career_field, doc["content"], doc["score"]):
                            results.append(RetrievedDocument(
                                id=doc["id"],
                                content=doc["content"],
                                doc_type="job_description",
                                score=doc["score"],
                                metadata=doc["metadata"]
                            ))
                        
                except Exception as e:
                    logger.warning(f"Failed to query job descriptions: {str(e)}")
            
            # Query reference documents (scoring criteria - always relevant)
            if include_reference:
                try:
                    ref_results = vector_store.query_similar(
                        collection_name=self._reference_collection,
                        query_embedding=query_embedding,
                        top_k=top_k
                    )
                    
                    for doc in ref_results:
                        # Reference docs don't need career field filtering
                        # but still apply minimum score threshold
                        if doc["score"] >= self._min_similarity_score:
                            results.append(RetrievedDocument(
                                id=doc["id"],
                                content=doc["content"],
                                doc_type="reference",
                                score=doc["score"],
                                metadata=doc["metadata"]
                            ))
                        
                except Exception as e:
                    logger.warning(f"Failed to query reference documents: {str(e)}")
            
            # Query job reference data from CSV
            if include_job_reference:
                try:
                    job_ref_results = vector_store.query_similar(
                        collection_name=COLLECTION_JOB_REFERENCE,
                        query_embedding=query_embedding,
                        top_k=top_k * 2  # Fetch more to allow for filtering
                    )
                    
                    for doc in job_ref_results:
                        # Apply relevance filtering to job reference data
                        if self.is_context_relevant(cv_career_field, doc["content"], doc["score"]):
                            results.append(RetrievedDocument(
                                id=doc["id"],
                                content=doc["content"],
                                doc_type="job_reference",
                                score=doc["score"],
                                metadata=doc["metadata"]
                            ))
                        
                except Exception as e:
                    logger.warning(f"Failed to query job reference data: {str(e)}")
            
            # Sort by score (highest first)
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Limit total results
            results = results[:top_k * 2]  # Allow some overlap
            
            elapsed_time = time.time() - start_time
            logger.info(
                f"RAG retrieval completed: {len(results)} docs in {elapsed_time:.2f}s "
                f"(CV field: {cv_career_field})"
            )
            
            # Performance check
            if elapsed_time > 2.0:
                logger.warning(f"RAG retrieval exceeded 2s threshold: {elapsed_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"RAG retrieval failed: {str(e)}")
            return []
    
    def format_context_for_prompt(
        self,
        documents: List[RetrievedDocument],
        max_chars: int = 4000
    ) -> str:
        """
        Format retrieved documents for inclusion in LLM prompt.
        
        Args:
            documents: List of retrieved documents
            max_chars: Maximum characters to include
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        sections = []
        current_chars = 0
        
        # Group by document type
        job_docs = [d for d in documents if d.doc_type == "job_description"]
        ref_docs = [d for d in documents if d.doc_type == "reference"]
        job_ref_docs = [d for d in documents if d.doc_type == "job_reference"]
        
        # Add job descriptions
        if job_docs:
            job_section = "## Relevant Job Descriptions:\n"
            for doc in job_docs[:3]:  # Limit to top 3
                title = doc.metadata.get("title", "Job")
                excerpt = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
                job_section += f"\n### {title}\n{excerpt}\n"
            
            if current_chars + len(job_section) < max_chars:
                sections.append(job_section)
                current_chars += len(job_section)
        
        # Add reference documents (scoring criteria)
        if ref_docs:
            ref_section = "\n## Scoring Guidelines:\n"
            for doc in ref_docs[:2]:  # Limit to top 2
                # Extract key sections from reference docs
                excerpt = self._extract_key_sections(doc.content, max_chars=1000)
                ref_section += f"\n{excerpt}\n"
            
            if current_chars + len(ref_section) < max_chars:
                sections.append(ref_section)
                current_chars += len(ref_section)
        
        # Add job reference data (from CSV - job requirements and career profiles)
        if job_ref_docs:
            job_ref_section = "\n## Job Market Reference Data:\n"
            for doc in job_ref_docs[:3]:  # Limit to top 3
                job_position = doc.metadata.get("job_position", "Position")
                excerpt = doc.content[:400] + "..." if len(doc.content) > 400 else doc.content
                job_ref_section += f"\n### {job_position}\n{excerpt}\n"
            
            if current_chars + len(job_ref_section) < max_chars:
                sections.append(job_ref_section)
        
        return "\n".join(sections)
    
    def _extract_key_sections(self, content: str, max_chars: int = 1000) -> str:
        """Extract key sections from reference document content."""
        # For scoring criteria, extract the scoring dimensions
        lines = content.split("\n")
        key_lines = []
        current_chars = 0
        
        for line in lines:
            # Prioritize headers and score ranges
            if line.startswith("#") or "points" in line.lower() or "score" in line.lower():
                if current_chars + len(line) < max_chars:
                    key_lines.append(line)
                    current_chars += len(line)
        
        if not key_lines:
            # Fallback: just truncate
            return content[:max_chars]
        
        return "\n".join(key_lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed documents."""
        return {
            "jobs_count": vector_store.get_collection_count(self._jobs_collection),
            "reference_count": vector_store.get_collection_count(self._reference_collection),
            "job_reference_count": vector_store.get_collection_count(COLLECTION_JOB_REFERENCE),
            "is_available": self.is_available,
            "reference_loaded": self._reference_docs_loaded
        }


# Global singleton instance
rag_service = RAGService()


# Convenience functions
def retrieve_context(cv_content: str, user_id: Optional[int] = None) -> List[RetrievedDocument]:
    """Retrieve relevant context for CV analysis."""
    return rag_service.retrieve_context(cv_content, user_id=user_id)


def format_context_for_prompt(documents: List[RetrievedDocument]) -> str:
    """Format retrieved documents for LLM prompt."""
    return rag_service.format_context_for_prompt(documents)
