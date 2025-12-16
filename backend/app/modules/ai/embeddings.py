"""
Embedding Service - Text Embeddings using Sentence Transformers.

This module provides embedding generation for the RAG pipeline,
supporting both Vietnamese and English text using a multilingual model.
"""

import logging
from typing import List, Optional
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy loading of sentence-transformers to avoid import overhead
_model = None
_model_loading = False


def _get_model():
    """
    Get or load the sentence transformer model.
    Uses lazy loading to avoid startup overhead.
    """
    global _model, _model_loading

    if _model is not None:
        return _model

    if _model_loading:
        # Avoid concurrent loading
        import time
        while _model_loading and _model is None:
            time.sleep(0.1)
        return _model

    try:
        _model_loading = True
        from sentence_transformers import SentenceTransformer

        model_name = settings.EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {model_name}")

        _model = SentenceTransformer(model_name)
        logger.info(f"Embedding model loaded successfully. Dimension: {
                    _model.get_sentence_embedding_dimension()}")

        return _model

    except Exception as e:
        logger.error(f"Failed to load embedding model: {str(e)}")
        _model_loading = False
        return None
    finally:
        _model_loading = False


class EmbeddingService:
    """
    Service for generating text embeddings using Sentence Transformers.

    Uses the paraphrase-multilingual-MiniLM-L12-v2 model which supports
    50+ languages including Vietnamese and English.
    """

    _instance: Optional["EmbeddingService"] = None

    def __new__(cls) -> "EmbeddingService":
        """Singleton pattern for embedding service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the embedding service."""
        self._model_name = settings.EMBEDDING_MODEL
        self._dimension: Optional[int] = None

    @property
    def model(self):
        """Get the loaded model (lazy loading)."""
        return _get_model()

    @property
    def is_available(self) -> bool:
        """Check if the embedding model is available."""
        return self.model is not None

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        if self._dimension is None and self.model is not None:
            self._dimension = self.model.get_sentence_embedding_dimension()
        return self._dimension or 384  # Default for MiniLM

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        if not self.is_available:
            logger.error("Embedding model not available")
            return None

        try:
            # Truncate very long texts to avoid memory issues
            max_length = 8192  # chars, model handles tokenization
            if len(text) > max_length:
                text = text[:max_length]
                logger.debug(f"Text truncated to {
                             max_length} chars for embedding")

            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return None

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once

        Returns:
            List of embeddings (None for failed texts)
        """
        if not texts:
            return []

        if not self.is_available:
            logger.error("Embedding model not available")
            return [None] * len(texts)

        try:
            # Filter and prepare texts
            processed_texts = []
            valid_indices = []
            max_length = 8192

            for i, text in enumerate(texts):
                if text and text.strip():
                    processed_text = text[:max_length] if len(
                        text) > max_length else text
                    processed_texts.append(processed_text)
                    valid_indices.append(i)

            if not processed_texts:
                return [None] * len(texts)

            # Generate embeddings in batch
            embeddings = self.model.encode(
                processed_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            # Map back to original indices
            results: List[Optional[List[float]]] = [None] * len(texts)
            for i, valid_idx in enumerate(valid_indices):
                results[valid_idx] = embeddings[i].tolist()

            logger.debug(f"Generated {len(valid_indices)} embeddings in batch")
            return results

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            return [None] * len(texts)

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            import numpy as np

            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity (embeddings are already normalized)
            similarity = np.dot(vec1, vec2)

            # Clamp to [0, 1] range
            return float(max(0.0, min(1.0, similarity)))

        except Exception as e:
            logger.error(f"Failed to compute similarity: {str(e)}")
            return 0.0


# Global singleton instance
embedding_service = EmbeddingService()


# Convenience functions
def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for a single text."""
    return embedding_service.generate_embedding(text)


def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """Generate embeddings for multiple texts."""
    return embedding_service.generate_embeddings_batch(texts)
