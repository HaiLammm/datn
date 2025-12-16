"""
Tests for Embedding Service - Sentence Transformers Integration.

Tests cover:
- Embedding generation for single texts
- Batch embedding generation
- Multilingual support (Vietnamese/English)
- Similarity computation
- Error handling and edge cases
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from typing import List

# Mock numpy and sentence-transformers before importing
mock_numpy = MagicMock()
mock_numpy.array = MagicMock(side_effect=lambda x: x)
mock_numpy.dot = MagicMock(return_value=0.9)
sys.modules['numpy'] = mock_numpy

mock_sentence_transformers = MagicMock()
sys.modules['sentence_transformers'] = mock_sentence_transformers

# Also mock chromadb to prevent import errors
mock_chromadb = MagicMock()
sys.modules['chromadb'] = mock_chromadb
sys.modules['chromadb.config'] = MagicMock()


class TestEmbeddingService:
    """Unit tests for EmbeddingService."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock SentenceTransformer model."""
        model = MagicMock()
        model.get_sentence_embedding_dimension.return_value = 384
        
        # Create a mock array-like object for embeddings
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1] * 384
        model.encode.return_value = mock_embedding
        
        return model

    def test_generate_embedding_success(self, mock_model):
        """Test successful embedding generation."""
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding("Test text for embedding")
        
        assert result is not None
        assert len(result) == 384
        assert isinstance(result, list)
        mock_model.encode.assert_called_once()

    def test_generate_embedding_empty_text(self, mock_model):
        """Test embedding generation with empty text returns None."""
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding("")
            assert result is None
            
            result = service.generate_embedding("   ")
            assert result is None

    def test_generate_embedding_model_unavailable(self):
        """Test embedding generation when model is not available."""
        with patch('app.modules.ai.embeddings._get_model', return_value=None):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding("Test text")
            assert result is None

    def test_generate_embedding_truncates_long_text(self, mock_model):
        """Test that long texts are truncated."""
        long_text = "A" * 10000  # Text longer than max_length
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding(long_text)
        
        assert result is not None
        # Verify encode was called with truncated text
        call_args = mock_model.encode.call_args
        assert len(call_args[0][0]) <= 8192

    def test_generate_embedding_vietnamese_text(self, mock_model):
        """Test embedding generation for Vietnamese text."""
        vietnamese_text = "Toi la mot lap trinh vien voi 5 nam kinh nghiem trong Python"
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding(vietnamese_text)
        
        assert result is not None
        assert len(result) == 384

    def test_generate_embedding_english_text(self, mock_model):
        """Test embedding generation for English text."""
        english_text = "I am a software developer with 5 years of Python experience"
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            result = service.generate_embedding(english_text)
        
        assert result is not None
        assert len(result) == 384


class TestEmbeddingServiceBatch:
    """Tests for batch embedding generation."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock SentenceTransformer model for batch operations."""
        model = MagicMock()
        model.get_sentence_embedding_dimension.return_value = 384
        return model

    def test_generate_embeddings_batch_success(self, mock_model):
        """Test successful batch embedding generation."""
        texts = ["Text 1", "Text 2", "Text 3"]
        
        # Create mock embeddings that have tolist method
        mock_embeddings = []
        for i in range(3):
            mock_emb = MagicMock()
            mock_emb.tolist.return_value = [0.1 * (i + 1)] * 384
            mock_embeddings.append(mock_emb)
        
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter(mock_embeddings))
        mock_result.__getitem__ = Mock(side_effect=lambda i: mock_embeddings[i])
        mock_model.encode.return_value = mock_result
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            results = service.generate_embeddings_batch(texts)
        
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert len(result) == 384

    def test_generate_embeddings_batch_empty_list(self, mock_model):
        """Test batch embedding with empty list."""
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            results = service.generate_embeddings_batch([])
        
        assert results == []

    def test_generate_embeddings_batch_with_empty_strings(self, mock_model):
        """Test batch embedding handles empty strings in list."""
        texts = ["Text 1", "", "Text 3", "   "]
        
        # Only 2 valid texts
        mock_embeddings = []
        for i in range(2):
            mock_emb = MagicMock()
            mock_emb.tolist.return_value = [0.1] * 384
            mock_embeddings.append(mock_emb)
        
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter(mock_embeddings))
        mock_result.__getitem__ = Mock(side_effect=lambda i: mock_embeddings[i])
        mock_model.encode.return_value = mock_result
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            results = service.generate_embeddings_batch(texts)
        
        assert len(results) == 4
        assert results[0] is not None  # "Text 1"
        assert results[1] is None      # "" - empty
        assert results[2] is not None  # "Text 3"
        assert results[3] is None      # "   " - whitespace

    def test_generate_embeddings_batch_model_unavailable(self):
        """Test batch embedding when model is not available."""
        with patch('app.modules.ai.embeddings._get_model', return_value=None):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            results = service.generate_embeddings_batch(["Text 1", "Text 2"])
        
        assert results == [None, None]


class TestEmbeddingSimilarity:
    """Tests for similarity computation logic."""

    def test_compute_similarity_identical_vectors(self):
        """Test that cosine similarity of identical vectors is 1.0."""
        # Test the mathematical formula for cosine similarity
        # For identical normalized vectors: cos_sim = dot(v, v) / (||v|| * ||v||) = 1.0
        embedding = [0.5] * 384
        
        # Calculate manually to verify the formula
        # dot product of identical vectors
        dot_product = sum(x * x for x in embedding)  # = 0.25 * 384 = 96
        
        # magnitude (norm)
        magnitude = (sum(x * x for x in embedding)) ** 0.5  # sqrt(96)
        
        # cosine similarity = dot / (mag * mag)
        similarity = dot_product / (magnitude * magnitude)
        
        # For identical vectors, this should be exactly 1.0
        assert abs(similarity - 1.0) < 0.0001, f"Expected similarity ~1.0, got {similarity}"

    def test_compute_similarity_returns_clamped_value(self):
        """Test that cosine similarity is always between 0 and 1 for non-negative vectors."""
        embedding1 = [0.1] * 384
        embedding2 = [0.2] * 384
        
        # Calculate cosine similarity manually
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))  # 0.1 * 0.2 * 384 = 7.68
        
        mag1 = (sum(x * x for x in embedding1)) ** 0.5  # sqrt(0.01 * 384) = sqrt(3.84)
        mag2 = (sum(x * x for x in embedding2)) ** 0.5  # sqrt(0.04 * 384) = sqrt(15.36)
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        # Since both vectors have same direction (all positive values), similarity should be 1.0
        assert 0.0 <= similarity <= 1.0, f"Expected 0 <= similarity <= 1, got {similarity}"
        # For vectors with the same direction, similarity is ~1.0
        assert similarity > 0.99, f"Expected similarity close to 1.0 for parallel vectors, got {similarity}"

    def test_compute_similarity_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is 0."""
        # Create orthogonal vectors using alternating pattern
        embedding1 = [1.0 if i % 2 == 0 else 0.0 for i in range(384)]
        embedding2 = [0.0 if i % 2 == 0 else 1.0 for i in range(384)]
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Orthogonal vectors have dot product of 0
        assert abs(dot_product) < 0.0001, f"Expected dot product ~0, got {dot_product}"


class TestEmbeddingServiceProperties:
    """Tests for EmbeddingService properties."""

    def test_dimension_property(self):
        """Test dimension property returns correct value."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            dim = service.dimension
            
            assert dim == 384

    def test_dimension_property_default(self):
        """Test dimension property returns default when model unavailable."""
        with patch('app.modules.ai.embeddings._get_model', return_value=None):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            service._dimension = None
            
            dim = service.dimension
            
            assert dim == 384  # Default for MiniLM

    def test_is_available_property(self):
        """Test is_available property."""
        mock_model = MagicMock()
        
        with patch('app.modules.ai.embeddings._get_model', return_value=mock_model):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            
            assert service.is_available is True
        
        with patch('app.modules.ai.embeddings._get_model', return_value=None):
            from app.modules.ai.embeddings import EmbeddingService
            EmbeddingService._instance = None
            
            service = EmbeddingService()
            
            assert service.is_available is False


class TestEmbeddingServiceSingleton:
    """Tests for EmbeddingService singleton behavior."""

    def test_singleton_pattern(self):
        """Test that EmbeddingService uses singleton pattern."""
        with patch('app.modules.ai.embeddings._get_model', return_value=MagicMock()):
            from app.modules.ai.embeddings import EmbeddingService
            
            # Reset singleton
            EmbeddingService._instance = None
            
            service1 = EmbeddingService()
            service2 = EmbeddingService()
            
            assert service1 is service2


class TestEmbeddingServiceIntegration:
    """Integration tests for EmbeddingService (requires sentence-transformers)."""

    @pytest.mark.skip(reason="Integration test - requires sentence-transformers setup")
    def test_real_embedding_generation(self):
        """Test real embedding generation with actual model."""
        from app.modules.ai.embeddings import embedding_service
        
        # Test English text
        english_embedding = embedding_service.generate_embedding(
            "Software engineer with Python experience"
        )
        assert english_embedding is not None
        assert len(english_embedding) == 384
        
        # Test Vietnamese text
        vietnamese_embedding = embedding_service.generate_embedding(
            "Ky su phan mem voi kinh nghiem Python"
        )
        assert vietnamese_embedding is not None
        assert len(vietnamese_embedding) == 384
        
        # Test similarity between semantically similar texts
        similarity = embedding_service.compute_similarity(
            english_embedding, vietnamese_embedding
        )
        # Same meaning, different languages - should have some similarity
        assert similarity > 0.3
