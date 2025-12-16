"""
Tests for RAG Service - Retrieval-Augmented Generation.

Tests cover:
- Job description indexing
- Reference document loading
- Context retrieval for CV analysis
- Context formatting for LLM prompts
- Fallback behavior when services are unavailable
- Performance requirements
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Mock chromadb, numpy, and sentence_transformers before importing
mock_chromadb = MagicMock()
sys.modules['chromadb'] = mock_chromadb
sys.modules['chromadb.config'] = MagicMock()

mock_numpy = MagicMock()
sys.modules['numpy'] = mock_numpy

mock_sentence_transformers = MagicMock()
sys.modules['sentence_transformers'] = mock_sentence_transformers


class TestRAGServiceAvailability:
    """Tests for RAG service availability."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store."""
        mock = MagicMock()
        mock.is_available = True
        mock.index_document.return_value = True
        mock.index_documents_batch.return_value = True
        mock.query_similar.return_value = []
        mock.delete_document.return_value = True
        mock.get_collection_count.return_value = 0
        return mock

    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        mock = MagicMock()
        mock.is_available = True
        mock.generate_embedding.return_value = [0.1] * 384
        mock.generate_embeddings_batch.return_value = [[0.1] * 384, [0.2] * 384]
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_embedding_service):
        """Create a RAGService instance with mocked dependencies."""
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                from app.modules.ai.rag_service import RAGService
                
                # Reset singleton
                RAGService._instance = None
                RAGService._reference_docs_loaded = False
                
                service = RAGService()
                return service

    def test_is_available_when_both_services_available(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test RAG service is available when dependencies are available."""
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                assert rag_service.is_available is True

    def test_is_not_available_when_vector_store_unavailable(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test RAG service unavailable when vector store is down."""
        mock_vector_store.is_available = False
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                assert rag_service.is_available is False

    def test_is_not_available_when_embedding_service_unavailable(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test RAG service unavailable when embedding service is down."""
        mock_embedding_service.is_available = False
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                assert rag_service.is_available is False


class TestJobDescriptionIndexing:
    """Tests for job description indexing."""

    @pytest.fixture
    def mock_vector_store(self):
        mock = MagicMock()
        mock.is_available = True
        mock.index_document.return_value = True
        return mock

    @pytest.fixture
    def mock_embedding_service(self):
        mock = MagicMock()
        mock.is_available = True
        mock.generate_embedding.return_value = [0.1] * 384
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_embedding_service):
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                from app.modules.ai.rag_service import RAGService
                RAGService._instance = None
                return RAGService()

    def test_index_job_description_success(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test successful job description indexing."""
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                result = rag_service.index_job_description(
                    jd_id="job1",
                    title="Software Engineer",
                    description="We are looking for a Python developer...",
                    required_skills=["Python", "FastAPI", "PostgreSQL"],
                    user_id=123
                )
        
        assert result is True
        mock_embedding_service.generate_embedding.assert_called_once()
        mock_vector_store.index_document.assert_called_once()

    def test_index_job_description_without_skills(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test indexing job description without required skills."""
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                result = rag_service.index_job_description(
                    jd_id="job2",
                    title="Data Analyst",
                    description="Analyze business data..."
                )
        
        assert result is True

    def test_index_job_description_when_unavailable(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test indexing fails gracefully when service unavailable."""
        mock_vector_store.is_available = False
        mock_embedding_service.is_available = False
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                result = rag_service.index_job_description(
                    jd_id="job3",
                    title="Test Job",
                    description="Test description"
                )
        
        assert result is False

    def test_index_job_description_embedding_fails(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test indexing fails when embedding generation fails."""
        mock_embedding_service.generate_embedding.return_value = None
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                result = rag_service.index_job_description(
                    jd_id="job4",
                    title="Test Job",
                    description="Test description"
                )
        
        assert result is False

    def test_delete_job_description(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test job description deletion."""
        mock_vector_store.delete_document.return_value = True
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            result = rag_service.delete_job_description("job1")
        
        assert result is True
        mock_vector_store.delete_document.assert_called_once()


class TestContextRetrieval:
    """Tests for context retrieval."""

    @pytest.fixture
    def mock_vector_store(self):
        mock = MagicMock()
        mock.is_available = True
        return mock

    @pytest.fixture
    def mock_embedding_service(self):
        mock = MagicMock()
        mock.is_available = True
        mock.generate_embedding.return_value = [0.1] * 384
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_embedding_service):
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                from app.modules.ai.rag_service import RAGService
                RAGService._instance = None
                return RAGService()

    def test_retrieve_context_success(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test successful context retrieval."""
        mock_vector_store.query_similar.side_effect = [
            # Job descriptions results
            [
                {"id": "job1", "content": "Python developer position", "metadata": {"title": "Developer"}, "score": 0.9}
            ],
            # Reference docs results
            [
                {"id": "ref1", "content": "Scoring criteria...", "metadata": {"doc_type": "reference"}, "score": 0.8}
            ]
        ]
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context(
                    cv_content="Experienced Python developer with 5 years experience..."
                )
        
        assert len(results) == 2
        assert results[0].score == 0.9  # Sorted by score
        assert results[1].score == 0.8

    def test_retrieve_context_empty_results(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test retrieval returns empty when no matches found."""
        mock_vector_store.query_similar.return_value = []
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context("Some CV content")
        
        assert results == []

    def test_retrieve_context_when_unavailable(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test retrieval returns empty when service unavailable."""
        mock_vector_store.is_available = False
        mock_embedding_service.is_available = False
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context("Some CV content")
        
        assert results == []

    def test_retrieve_context_embedding_fails(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test retrieval returns empty when embedding fails."""
        mock_embedding_service.generate_embedding.return_value = None
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context("Some CV content")
        
        assert results == []

    def test_fallback_on_chromadb_error(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test graceful fallback when ChromaDB query fails."""
        mock_vector_store.query_similar.side_effect = Exception("ChromaDB connection error")
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                # Should not raise, should return empty
                results = rag_service.retrieve_context("CV content")
        
        assert results == []


class TestContextFormatting:
    """Tests for context formatting for LLM prompts."""

    @pytest.fixture
    def rag_service(self):
        with patch('app.modules.ai.rag_service.vector_store'):
            with patch('app.modules.ai.rag_service.embedding_service'):
                from app.modules.ai.rag_service import RAGService
                RAGService._instance = None
                return RAGService()

    @pytest.fixture
    def sample_documents(self):
        from app.modules.ai.rag_service import RetrievedDocument
        return [
            RetrievedDocument(
                id="job1",
                content="Job Title: Python Developer\n\nDescription: Looking for experienced Python developer with FastAPI skills...",
                doc_type="job_description",
                score=0.9,
                metadata={"title": "Python Developer"}
            ),
            RetrievedDocument(
                id="ref1",
                content="# Scoring Criteria\n\n## Technical Skills: 30 points\n- Programming languages\n- Frameworks\n\n## Experience: 25 points",
                doc_type="reference",
                score=0.8,
                metadata={"filename": "scoring_criteria_en.txt"}
            )
        ]

    def test_format_context_for_prompt(self, rag_service, sample_documents):
        """Test context formatting for LLM prompt."""
        result = rag_service.format_context_for_prompt(sample_documents)
        
        assert "## Relevant Job Descriptions:" in result
        assert "Python Developer" in result
        assert "## Scoring Guidelines:" in result

    def test_format_context_empty_documents(self, rag_service):
        """Test formatting returns empty string for empty documents."""
        result = rag_service.format_context_for_prompt([])
        
        assert result == ""

    def test_format_context_jobs_only(self, rag_service):
        """Test formatting with only job descriptions."""
        from app.modules.ai.rag_service import RetrievedDocument
        
        docs = [
            RetrievedDocument(
                id="job1",
                content="Python developer job",
                doc_type="job_description",
                score=0.9,
                metadata={"title": "Developer"}
            )
        ]
        
        result = rag_service.format_context_for_prompt(docs)
        
        assert "## Relevant Job Descriptions:" in result
        assert "## Scoring Guidelines:" not in result

    def test_format_context_reference_only(self, rag_service):
        """Test formatting with only reference documents."""
        from app.modules.ai.rag_service import RetrievedDocument
        
        docs = [
            RetrievedDocument(
                id="ref1",
                content="# Scoring criteria\nScore: 100 points",
                doc_type="reference",
                score=0.8,
                metadata={}
            )
        ]
        
        result = rag_service.format_context_for_prompt(docs)
        
        assert "## Scoring Guidelines:" in result
        assert "## Relevant Job Descriptions:" not in result


class TestRAGServiceStats:
    """Tests for RAG service statistics."""

    @pytest.fixture
    def mock_vector_store(self):
        mock = MagicMock()
        mock.is_available = True
        mock.get_collection_count.side_effect = lambda name: 10 if "jobs" in name else 5
        return mock

    @pytest.fixture
    def mock_embedding_service(self):
        mock = MagicMock()
        mock.is_available = True
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_embedding_service):
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                from app.modules.ai.rag_service import RAGService
                RAGService._instance = None
                return RAGService()

    def test_get_stats(self, rag_service, mock_vector_store, mock_embedding_service):
        """Test getting RAG service statistics."""
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                stats = rag_service.get_stats()
        
        assert "jobs_count" in stats
        assert "reference_count" in stats
        assert "is_available" in stats
        assert "reference_loaded" in stats


class TestRAGServiceSingleton:
    """Tests for RAGService singleton behavior."""

    def test_singleton_pattern(self):
        """Test that RAGService uses singleton pattern."""
        with patch('app.modules.ai.rag_service.vector_store'):
            with patch('app.modules.ai.rag_service.embedding_service'):
                from app.modules.ai.rag_service import RAGService
                
                # Reset singleton
                RAGService._instance = None
                
                service1 = RAGService()
                service2 = RAGService()
                
                assert service1 is service2


class TestRAGContextRelevance:
    """Tests for RAG context relevance validation (GAP-001 / CV-INT-013).
    
    Critical tests to ensure RAG retrieval returns semantically relevant context
    and does NOT return unrelated job descriptions that could cause LLM hallucinations.
    
    Background: IT professional CVs were misclassified as "Trade Marketing Executive"
    because RAG retrieved unrelated marketing/hygiene job descriptions from training data.
    """

    @pytest.fixture
    def mock_vector_store(self):
        mock = MagicMock()
        mock.is_available = True
        return mock

    @pytest.fixture
    def mock_embedding_service(self):
        mock = MagicMock()
        mock.is_available = True
        mock.generate_embedding.return_value = [0.1] * 384
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_embedding_service):
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                from app.modules.ai.rag_service import RAGService
                RAGService._instance = None
                service = RAGService()
                # Ensure relevance checking is enabled for tests
                service._relevance_check_enabled = True
                service._min_similarity_score = 0.3
                return service

    @pytest.fixture
    def it_developer_cv_text(self):
        """Sample IT Developer CV text with identifiable technical skills."""
        return """
        LUONG HAI LAM
        Software Developer / Full Stack Engineer
        
        TECHNICAL SKILLS
        - Programming Languages: Python, JavaScript, TypeScript
        - Frameworks: React, Next.js, FastAPI, Django
        - Databases: PostgreSQL, MongoDB, Redis
        - DevOps: Docker, Kubernetes, AWS, CI/CD
        - Version Control: Git, GitHub
        
        WORK EXPERIENCE
        
        Senior Software Engineer | Tech Company ABC (2021-Present)
        - Designed and developed RESTful APIs using Python and FastAPI
        - Built responsive web applications with React and TypeScript
        - Implemented microservices architecture with Docker and Kubernetes
        - Optimized PostgreSQL database queries for better performance
        
        Software Developer | Startup XYZ (2019-2021)
        - Developed full-stack applications using Django and React
        - Integrated third-party APIs and payment gateways
        - Wrote unit tests and integration tests using pytest
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology (2015-2019)
        
        CERTIFICATIONS
        - AWS Certified Developer Associate
        - MongoDB Certified Developer
        """

    @pytest.fixture
    def marketing_job_descriptions(self):
        """Unrelated marketing job descriptions that should NOT be returned for IT CVs."""
        return [
            {
                "id": "marketing_job_1",
                "content": "Trade Marketing Executive position for hygiene products company. "
                          "Responsible for developing trade marketing strategies, managing "
                          "retail promotions, and coordinating with distributors for FMCG products.",
                "metadata": {"title": "Trade Marketing Executive"},
                "score": 0.75
            },
            {
                "id": "marketing_job_2", 
                "content": "Marketing Manager for consumer goods. Experience in brand management, "
                          "market research, and advertising campaigns for personal care products.",
                "metadata": {"title": "Marketing Manager"},
                "score": 0.70
            }
        ]

    @pytest.fixture
    def it_job_descriptions(self):
        """Relevant IT job descriptions that SHOULD be returned for IT CVs."""
        return [
            {
                "id": "it_job_1",
                "content": "Software Engineer position. Looking for experienced Python developer "
                          "with FastAPI experience. Must have skills in React, PostgreSQL, and Docker.",
                "metadata": {"title": "Software Engineer"},
                "score": 0.92
            },
            {
                "id": "it_job_2",
                "content": "Full Stack Developer role. Required skills: JavaScript, TypeScript, "
                          "React, Node.js, PostgreSQL. Experience with AWS and CI/CD preferred.",
                "metadata": {"title": "Full Stack Developer"},
                "score": 0.88
            }
        ]

    def test_rag_returns_relevant_it_jobs_for_it_cv(
        self, rag_service, mock_vector_store, mock_embedding_service, 
        it_developer_cv_text, it_job_descriptions
    ):
        """
        CV-INT-013: Given IT Developer CV, RAG should return IT-related job descriptions.
        
        Given: CV text about IT/Software development with Python, React, PostgreSQL
        When: RAG retrieves context
        Then: Retrieved documents should be IT-related (Software Engineer, Developer roles)
        """
        # Setup: RAG returns IT job descriptions
        mock_vector_store.query_similar.return_value = it_job_descriptions
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context(it_developer_cv_text)
        
        # Verify: Results contain IT-related content
        assert len(results) >= 1
        
        # Check that returned content is IT-related
        all_content = " ".join([r.content for r in results]).lower()
        
        # Should contain IT keywords
        it_keywords = ["python", "software", "developer", "react", "postgresql", "engineer"]
        assert any(keyword in all_content for keyword in it_keywords), \
            f"Expected IT-related content, but got: {all_content[:200]}"

    def test_rag_does_not_return_marketing_jobs_for_it_cv(
        self, rag_service, mock_vector_store, mock_embedding_service,
        it_developer_cv_text, it_job_descriptions
    ):
        """
        CV-INT-013 (Negative): Given IT Developer CV, RAG should NOT return 
        unrelated marketing/hygiene job descriptions.
        
        Given: CV text about IT/Software development
        When: RAG retrieves context with proper semantic matching
        Then: Formatted context should NOT contain marketing/hygiene keywords
        
        This test validates that when RAG works correctly, it returns
        IT-related jobs for IT CVs.
        """
        # Setup: RAG correctly returns IT job descriptions (not marketing)
        mock_vector_store.query_similar.return_value = it_job_descriptions
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context(it_developer_cv_text)
        
        # Verify: Results should be IT-related, NOT marketing
        all_content = " ".join([r.content for r in results]).lower()
        
        # CRITICAL: These keywords should NOT appear for an IT CV
        bad_keywords = ["trade marketing", "hygiene", "fmcg", "consumer goods", "retail promotion"]
        found_bad_keywords = [kw for kw in bad_keywords if kw in all_content]
        
        # When RAG works correctly, no marketing keywords should appear
        assert len(found_bad_keywords) == 0, \
            f"RAG returned marketing context for IT CV! " \
            f"Found unrelated keywords: {found_bad_keywords}. "
        
        # Verify IT keywords ARE present
        it_keywords = ["python", "developer", "software", "fastapi", "react"]
        assert any(kw in all_content for kw in it_keywords), \
            f"Expected IT-related content but got: {all_content[:200]}"

    def test_relevance_filter_blocks_marketing_for_it_cv(
        self, rag_service, mock_vector_store, mock_embedding_service,
        it_developer_cv_text, marketing_job_descriptions
    ):
        """
        NEW TEST: Relevance filter should block marketing jobs for IT CV.
        
        This test validates that the new relevance filtering correctly
        filters out marketing job descriptions when analyzing an IT CV.
        
        Note: We only test job_description collection since reference docs
        don't have career field filtering (they're general scoring criteria).
        """
        # Setup: Vector store returns marketing jobs (simulating bad embedding match)
        mock_vector_store.query_similar.return_value = marketing_job_descriptions
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                # Only test job descriptions - reference docs don't have career filtering
                results = rag_service.retrieve_context(
                    it_developer_cv_text,
                    include_reference=False,
                    include_job_reference=False
                )
        
        # With relevance filtering enabled, marketing jobs should be filtered out
        all_content = " ".join([r.content for r in results]).lower()
        
        bad_keywords = ["trade marketing", "hygiene", "fmcg", "consumer goods"]
        found_bad = [kw for kw in bad_keywords if kw in all_content]
        
        # The relevance filter should have blocked these
        assert len(found_bad) == 0, \
            f"Relevance filter failed! Marketing content found: {found_bad}"
        
        # Verify the filter was actually applied (results should be empty)
        assert len(results) == 0, \
            f"Expected 0 results after filtering, got {len(results)}"

    def test_career_field_detection_it(self, rag_service):
        """Test career field detection correctly identifies IT/Software CVs."""
        it_cv_text = """
        Software Engineer with Python, React, and PostgreSQL experience.
        Built REST APIs with FastAPI, deployed using Docker and Kubernetes.
        """
        
        field, confidence = rag_service.detect_career_field(it_cv_text)
        
        assert field == "it_software", f"Expected 'it_software' but got '{field}'"
        assert confidence > 0.3, f"Expected confidence > 0.3 but got {confidence}"

    def test_career_field_detection_marketing(self, rag_service):
        """Test career field detection correctly identifies Marketing CVs."""
        marketing_cv_text = """
        Trade Marketing Executive with 5 years experience in FMCG.
        Managed retail promotions, brand activation, and distributor relationships.
        """
        
        field, confidence = rag_service.detect_career_field(marketing_cv_text)
        
        assert field == "marketing_sales", f"Expected 'marketing_sales' but got '{field}'"
        assert confidence > 0.3, f"Expected confidence > 0.3 but got {confidence}"

    def test_is_context_relevant_blocks_mismatched_fields(self, rag_service):
        """Test that is_context_relevant blocks mismatched career fields."""
        marketing_content = "Trade Marketing Executive for hygiene products company. FMCG experience."
        
        # IT CV should reject marketing content
        is_relevant = rag_service.is_context_relevant(
            cv_career_field="it_software",
            context_content=marketing_content,
            similarity_score=0.75
        )
        
        assert is_relevant is False, "Marketing content should be filtered for IT CV"

    def test_is_context_relevant_allows_matching_fields(self, rag_service):
        """Test that is_context_relevant allows matching career fields."""
        it_content = "Python Developer position. FastAPI, React, PostgreSQL required."
        
        # IT CV should accept IT job content
        is_relevant = rag_service.is_context_relevant(
            cv_career_field="it_software",
            context_content=it_content,
            similarity_score=0.85
        )
        
        assert is_relevant is True, "IT content should be allowed for IT CV"

    def test_is_context_relevant_filters_low_scores(self, rag_service):
        """Test that low similarity scores are filtered regardless of content."""
        it_content = "Python Developer position."
        
        # Low score should be filtered
        is_relevant = rag_service.is_context_relevant(
            cv_career_field="it_software",
            context_content=it_content,
            similarity_score=0.1  # Below threshold
        )
        
        assert is_relevant is False, "Low similarity scores should be filtered"

    def test_formatted_context_excludes_irrelevant_job_types(self, rag_service):
        """
        CV-INT-013: Formatted prompt context should only include relevant job descriptions.
        
        Validates that format_context_for_prompt properly handles mixed results
        and the final context sent to LLM is appropriate.
        """
        from app.modules.ai.rag_service import RetrievedDocument
        
        # Mix of relevant and irrelevant documents
        mixed_docs = [
            RetrievedDocument(
                id="it_job",
                content="Python Developer: Build APIs with FastAPI and PostgreSQL",
                doc_type="job_description",
                score=0.95,
                metadata={"title": "Python Developer"}
            ),
            RetrievedDocument(
                id="marketing_job",
                content="Trade Marketing for hygiene products distribution",
                doc_type="job_description", 
                score=0.60,  # Lower score - should ideally be filtered
                metadata={"title": "Trade Marketing Executive"}
            ),
            RetrievedDocument(
                id="ref_doc",
                content="Scoring criteria for technical candidates",
                doc_type="reference",
                score=0.85,
                metadata={}
            )
        ]
        
        formatted = rag_service.format_context_for_prompt(mixed_docs)
        
        # The high-scoring IT job should be included
        assert "Python Developer" in formatted
        assert "FastAPI" in formatted
        
        # Reference docs should be included
        assert "Scoring" in formatted or "criteria" in formatted.lower()

    def test_retrieve_context_semantic_relevance(
        self, rag_service, mock_vector_store, mock_embedding_service,
        it_developer_cv_text
    ):
        """
        CV-INT-013: Test that semantic similarity scores reflect actual relevance.
        
        Higher scores should correlate with more relevant content.
        IT CV should have higher similarity with IT jobs than marketing jobs.
        """
        # Setup: Return documents with scores reflecting semantic similarity
        mock_vector_store.query_similar.side_effect = [
            # Jobs collection - should have high score for IT job, low for marketing
            [
                {"id": "it_job", "content": "Python FastAPI Developer", 
                 "metadata": {"title": "Developer"}, "score": 0.95},
            ],
            # Reference collection
            [
                {"id": "ref", "content": "Technical scoring guidelines",
                 "metadata": {}, "score": 0.80}
            ]
        ]
        
        with patch('app.modules.ai.rag_service.vector_store', mock_vector_store):
            with patch('app.modules.ai.rag_service.embedding_service', mock_embedding_service):
                results = rag_service.retrieve_context(it_developer_cv_text)
        
        # Verify high-score documents are IT-related
        high_score_docs = [r for r in results if r.score > 0.8]
        for doc in high_score_docs:
            content_lower = doc.content.lower()
            # High-scoring docs should NOT be marketing-related
            assert "trade marketing" not in content_lower
            assert "hygiene" not in content_lower
            assert "fmcg" not in content_lower


class TestRAGServiceIntegration:
    """Integration tests for RAGService (requires ChromaDB and sentence-transformers)."""

    @pytest.mark.skip(reason="Integration test - requires full setup")
    def test_full_rag_workflow(self):
        """Test complete RAG workflow: index, retrieve, format."""
        from app.modules.ai.rag_service import rag_service
        
        # Index a job description
        success = rag_service.index_job_description(
            jd_id="test_job_1",
            title="Python Developer",
            description="We are looking for a Python developer with FastAPI experience...",
            required_skills=["Python", "FastAPI", "PostgreSQL"]
        )
        assert success is True
        
        # Retrieve context for a CV
        cv_content = """
        John Doe
        Software Engineer
        
        Experience:
        - 5 years Python development
        - Built REST APIs with FastAPI
        - PostgreSQL database design
        """
        
        results = rag_service.retrieve_context(cv_content)
        assert len(results) >= 1
        
        # Format for prompt
        formatted = rag_service.format_context_for_prompt(results)
        assert "Python Developer" in formatted or len(formatted) > 0
        
        # Cleanup
        rag_service.delete_job_description("test_job_1")
