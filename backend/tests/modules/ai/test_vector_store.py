"""
Tests for Vector Store Service - ChromaDB Integration.

Tests cover:
- ChromaDB connection and health check
- Document indexing (single and batch)
- Semantic similarity search
- Document deletion
- Fallback behavior when ChromaDB is unavailable
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

# Mock chromadb before importing any modules that depend on it
mock_chromadb = MagicMock()
mock_chromadb_config = MagicMock()
mock_chromadb.config = mock_chromadb_config
sys.modules['chromadb'] = mock_chromadb
sys.modules['chromadb.config'] = mock_chromadb_config


class TestVectorStoreService:
    """Unit tests for VectorStoreService."""

    @pytest.fixture
    def mock_chromadb_client(self):
        """Create a mock ChromaDB client."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client.list_collections.return_value = []
        return mock_client, mock_collection

    @pytest.fixture
    def vector_store_service(self, mock_chromadb_client):
        """Create a VectorStoreService instance with mocked ChromaDB."""
        mock_client, _ = mock_chromadb_client
        
        mock_chromadb.PersistentClient = MagicMock(return_value=mock_client)
        
        with patch('app.modules.ai.vector_store.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.mkdir = MagicMock()
            
            # Import fresh to get new singleton
            from app.modules.ai.vector_store import VectorStoreService
            
            # Reset singleton for testing
            VectorStoreService._instance = None
            VectorStoreService._client = None
            VectorStoreService._is_available = False
            
            service = VectorStoreService()
            return service

    def test_chromadb_connection(self, mock_chromadb_client):
        """Test that ChromaDB connection is established successfully."""
        mock_client, _ = mock_chromadb_client
        
        mock_chromadb.PersistentClient = MagicMock(return_value=mock_client)
        
        with patch('app.modules.ai.vector_store.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            
            from app.modules.ai.vector_store import VectorStoreService
            
            # Reset singleton
            VectorStoreService._instance = None
            VectorStoreService._client = None
            VectorStoreService._is_available = False
            
            service = VectorStoreService()
            
            assert service.is_available is True

    def test_health_check_success(self, vector_store_service, mock_chromadb_client):
        """Test health check returns True when ChromaDB is healthy."""
        mock_client, _ = mock_chromadb_client
        mock_client.list_collections.return_value = []
        
        # Manually set the client for the test
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        assert vector_store_service.health_check() is True
        mock_client.list_collections.assert_called_once()

    def test_health_check_failure(self, vector_store_service, mock_chromadb_client):
        """Test health check returns False when ChromaDB is unhealthy."""
        mock_client, _ = mock_chromadb_client
        mock_client.list_collections.side_effect = Exception("Connection failed")
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        assert vector_store_service.health_check() is False
        assert vector_store_service._is_available is False

    def test_index_document_success(self, vector_store_service, mock_chromadb_client):
        """Test successful document indexing."""
        mock_client, mock_collection = mock_chromadb_client
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        embedding = [0.1] * 384  # 384-dimensional embedding
        
        result = vector_store_service.index_document(
            collection_name="test_collection",
            doc_id="doc1",
            content="Test document content",
            embedding=embedding,
            metadata={"title": "Test"}
        )
        
        assert result is True
        mock_collection.upsert.assert_called_once()

    def test_index_document_when_unavailable(self, vector_store_service):
        """Test document indexing when ChromaDB is unavailable."""
        vector_store_service._is_available = False
        
        result = vector_store_service.index_document(
            collection_name="test_collection",
            doc_id="doc1",
            content="Test content",
            embedding=[0.1] * 384
        )
        
        assert result is False

    def test_index_documents_batch(self, vector_store_service, mock_chromadb_client):
        """Test batch document indexing."""
        mock_client, mock_collection = mock_chromadb_client
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        doc_ids = ["doc1", "doc2", "doc3"]
        contents = ["Content 1", "Content 2", "Content 3"]
        embeddings = [[0.1] * 384 for _ in range(3)]
        metadatas = [{"id": i} for i in range(3)]
        
        result = vector_store_service.index_documents_batch(
            collection_name="test_collection",
            doc_ids=doc_ids,
            contents=contents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        assert result is True
        mock_collection.upsert.assert_called_once()

    def test_index_documents_batch_empty(self, vector_store_service, mock_chromadb_client):
        """Test batch indexing with empty list."""
        mock_client, _ = mock_chromadb_client
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        result = vector_store_service.index_documents_batch(
            collection_name="test_collection",
            doc_ids=[],
            contents=[],
            embeddings=[]
        )
        
        assert result is True  # Empty batch is a success (nothing to do)

    def test_query_similar_success(self, vector_store_service, mock_chromadb_client):
        """Test semantic similarity search."""
        mock_client, mock_collection = mock_chromadb_client
        
        # Configure mock to return results
        mock_collection.count.return_value = 5
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["Content 1", "Content 2"]],
            "metadatas": [[{"title": "Doc 1"}, {"title": "Doc 2"}]],
            "distances": [[0.1, 0.3]]
        }
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        query_embedding = [0.1] * 384
        
        results = vector_store_service.query_similar(
            collection_name="test_collection",
            query_embedding=query_embedding,
            top_k=5
        )
        
        assert len(results) == 2
        assert results[0]["id"] == "doc1"
        assert results[0]["content"] == "Content 1"
        assert results[0]["score"] == 0.9  # 1 - 0.1 distance
        assert results[1]["score"] == 0.7  # 1 - 0.3 distance

    def test_query_similar_empty_collection(self, vector_store_service, mock_chromadb_client):
        """Test query on empty collection returns empty results."""
        mock_client, mock_collection = mock_chromadb_client
        mock_collection.count.return_value = 0
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        results = vector_store_service.query_similar(
            collection_name="test_collection",
            query_embedding=[0.1] * 384,
            top_k=5
        )
        
        assert results == []

    def test_query_similar_when_unavailable(self, vector_store_service):
        """Test query when ChromaDB is unavailable."""
        vector_store_service._is_available = False
        
        results = vector_store_service.query_similar(
            collection_name="test_collection",
            query_embedding=[0.1] * 384,
            top_k=5
        )
        
        assert results == []

    def test_query_similar_with_filter(self, vector_store_service, mock_chromadb_client):
        """Test semantic search with metadata filter."""
        mock_client, mock_collection = mock_chromadb_client
        mock_collection.count.return_value = 3
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Filtered content"]],
            "metadatas": [[{"user_id": "123"}]],
            "distances": [[0.2]]
        }
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        results = vector_store_service.query_similar(
            collection_name="test_collection",
            query_embedding=[0.1] * 384,
            top_k=5,
            where_filter={"user_id": "123"}
        )
        
        assert len(results) == 1
        assert results[0]["metadata"]["user_id"] == "123"
        mock_collection.query.assert_called_with(
            query_embeddings=[[0.1] * 384],
            n_results=3,  # min(top_k, count)
            where={"user_id": "123"},
            include=["documents", "metadatas", "distances"]
        )

    def test_delete_document_success(self, vector_store_service, mock_chromadb_client):
        """Test successful document deletion."""
        mock_client, mock_collection = mock_chromadb_client
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        result = vector_store_service.delete_document(
            collection_name="test_collection",
            doc_id="doc1"
        )
        
        assert result is True
        mock_collection.delete.assert_called_once_with(ids=["doc1"])

    def test_delete_document_when_unavailable(self, vector_store_service):
        """Test document deletion when ChromaDB is unavailable."""
        vector_store_service._is_available = False
        
        result = vector_store_service.delete_document(
            collection_name="test_collection",
            doc_id="doc1"
        )
        
        assert result is False

    def test_get_collection_count(self, vector_store_service, mock_chromadb_client):
        """Test getting collection document count."""
        mock_client, mock_collection = mock_chromadb_client
        mock_collection.count.return_value = 42
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        count = vector_store_service.get_collection_count("test_collection")
        
        assert count == 42

    def test_get_collection_count_when_unavailable(self, vector_store_service):
        """Test collection count when ChromaDB is unavailable."""
        vector_store_service._is_available = False
        
        count = vector_store_service.get_collection_count("test_collection")
        
        assert count == 0

    def test_reset(self, vector_store_service, mock_chromadb_client):
        """Test resetting all collections."""
        mock_client, _ = mock_chromadb_client
        
        vector_store_service._client = mock_client
        vector_store_service._is_available = True
        
        result = vector_store_service.reset()
        
        assert result is True
        mock_client.reset.assert_called_once()


class TestVectorStoreSingleton:
    """Tests for VectorStoreService singleton behavior."""

    def test_singleton_pattern(self):
        """Test that VectorStoreService uses singleton pattern."""
        mock_chromadb.PersistentClient = MagicMock()
        
        with patch('app.modules.ai.vector_store.Path'):
            from app.modules.ai.vector_store import VectorStoreService
            
            # Reset singleton
            VectorStoreService._instance = None
            VectorStoreService._client = None
            
            service1 = VectorStoreService()
            service2 = VectorStoreService()
            
            assert service1 is service2


class TestVectorStoreIntegration:
    """Integration tests for VectorStoreService (requires ChromaDB)."""

    @pytest.mark.skip(reason="Integration test - requires ChromaDB setup")
    def test_full_workflow(self):
        """Test complete workflow: index, query, delete."""
        from app.modules.ai.vector_store import vector_store
        
        # Index a document
        embedding = [0.1] * 384
        success = vector_store.index_document(
            collection_name="test_integration",
            doc_id="test_doc_1",
            content="Python developer with 5 years experience",
            embedding=embedding,
            metadata={"title": "Software Engineer"}
        )
        assert success is True
        
        # Query for similar documents
        results = vector_store.query_similar(
            collection_name="test_integration",
            query_embedding=embedding,
            top_k=5
        )
        assert len(results) >= 1
        assert results[0]["id"] == "test_doc_1"
        
        # Delete the document
        delete_success = vector_store.delete_document(
            collection_name="test_integration",
            doc_id="test_doc_1"
        )
        assert delete_success is True
