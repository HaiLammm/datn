"""
Vector Store Service - ChromaDB Integration for RAG Pipeline.

This module provides a wrapper around ChromaDB for storing and retrieving
vector embeddings of job descriptions and reference documents.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service for managing ChromaDB vector store operations.
    
    Provides methods to:
    - Initialize and manage ChromaDB client
    - Index documents with embeddings
    - Query for similar documents
    - Health check and fallback handling
    """
    
    _instance: Optional["VectorStoreService"] = None
    _client: Optional[chromadb.ClientAPI] = None
    _is_available: bool = False
    
    def __new__(cls) -> "VectorStoreService":
        """Singleton pattern for vector store service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the vector store service."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client with persistent storage."""
        try:
            # Ensure persistence directory exists
            persist_path = Path(settings.CHROMA_PERSIST_PATH)
            persist_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB with persistent storage
            self._client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self._is_available = True
            logger.info(f"ChromaDB initialized at {persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self._is_available = False
            self._client = None
    
    @property
    def is_available(self) -> bool:
        """Check if ChromaDB is available."""
        return self._is_available and self._client is not None
    
    def health_check(self) -> bool:
        """
        Perform health check on ChromaDB connection.
        
        Returns:
            True if ChromaDB is healthy, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            # Try to list collections as a health check
            self._client.list_collections()
            return True
        except Exception as e:
            logger.warning(f"ChromaDB health check failed: {str(e)}")
            self._is_available = False
            return False
    
    def get_or_create_collection(
        self,
        collection_name: str,
        embedding_function: Optional[Any] = None
    ) -> Optional[chromadb.Collection]:
        """
        Get or create a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            embedding_function: Optional custom embedding function
            
        Returns:
            ChromaDB Collection or None if unavailable
        """
        if not self.is_available:
            logger.warning("ChromaDB not available, cannot get collection")
            return None
        
        try:
            collection = self._client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.debug(f"Got/created collection: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get/create collection {collection_name}: {str(e)}")
            return None
    
    def index_document(
        self,
        collection_name: str,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a document with its embedding into ChromaDB.
        
        Args:
            collection_name: Target collection name
            doc_id: Unique document identifier
            content: Document text content
            embedding: Pre-computed embedding vector
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("ChromaDB not available, cannot index document")
            return False
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                return False
            
            # Upsert to handle both new and existing documents
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}]
            )
            
            logger.debug(f"Indexed document {doc_id} to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {str(e)}")
            return False
    
    def index_documents_batch(
        self,
        collection_name: str,
        doc_ids: List[str],
        contents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Index multiple documents in batch.
        
        Args:
            collection_name: Target collection name
            doc_ids: List of document identifiers
            contents: List of document contents
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("ChromaDB not available, cannot batch index")
            return False
        
        if not doc_ids:
            return True  # Nothing to index
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                return False
            
            collection.upsert(
                ids=doc_ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas or [{} for _ in doc_ids]
            )
            
            logger.info(f"Batch indexed {len(doc_ids)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to batch index documents: {str(e)}")
            return False
    
    def query_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query for similar documents using embedding similarity.
        
        Args:
            collection_name: Collection to query
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where_filter: Optional metadata filter
            
        Returns:
            List of similar documents with scores
        """
        if not self.is_available:
            logger.warning("ChromaDB not available, returning empty results")
            return []
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                return []
            
            # Check if collection has any documents
            if collection.count() == 0:
                logger.debug(f"Collection {collection_name} is empty")
                return []
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count()),
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results and results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = {
                        "id": doc_id,
                        "content": results["documents"][0][i] if results.get("documents") else "",
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0.0,
                        "score": 1.0 - results["distances"][0][i] if results.get("distances") else 1.0
                    }
                    documents.append(doc)
            
            logger.debug(f"Query returned {len(documents)} results from {collection_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to query {collection_name}: {str(e)}")
            return []
    
    def delete_document(
        self,
        collection_name: str,
        doc_id: str
    ) -> bool:
        """
        Delete a document from a collection.
        
        Args:
            collection_name: Collection containing the document
            doc_id: Document identifier to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                return False
            
            collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document {doc_id} from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {str(e)}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        if not self.is_available:
            return 0
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                return 0
            return collection.count()
        except Exception:
            return 0
    
    def reset(self) -> bool:
        """
        Reset all collections (for testing purposes).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self._client.reset()
            logger.warning("ChromaDB reset - all collections deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB: {str(e)}")
            return False


# Global singleton instance
vector_store = VectorStoreService()
