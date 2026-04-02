"""
ChromaDB storage interface for knowledge base chunks.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings

from ..schemas.models import CleanChunk, QueryResult

logger = logging.getLogger(__name__)


class ChromaKBStore:
    """
    Interface for storing and querying knowledge base chunks in ChromaDB.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "kb_poc"):
        """
        Initialize ChromaDB storage.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"Initialized ChromaDB store at {self.persist_directory} with collection '{self.collection_name}'")
    
    def add_chunks(self, chunks: List[CleanChunk]) -> int:
        """
        Add chunks to the ChromaDB collection.
        
        Args:
            chunks: List of CleanChunk objects to store
            
        Returns:
            Number of chunks successfully added
        """
        if not chunks:
            logger.warning("No chunks to add")
            return 0
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        embeddings = []
        metadatas = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                logger.warning(f"Chunk {chunk.chunk_id} has no embedding, skipping")
                continue
            
            ids.append(chunk.chunk_id)
            documents.append(chunk.content)
            embeddings.append(chunk.embedding)
            
            # Prepare metadata (ChromaDB requires flat dict with basic types)
            metadata = {
                "document_id": chunk.document_id,
                "source_url": chunk.source_url,
                "chunk_index": chunk.chunk_index,
                "word_count": chunk.word_count,
                "created_at": chunk.created_at.isoformat(),
            }
            
            # Add custom metadata fields
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
            
            metadatas.append(metadata)
        
        if not ids:
            logger.warning("No valid chunks with embeddings to add")
            return 0
        
        # Add to ChromaDB
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(ids)} chunks to collection '{self.collection_name}'")
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {e}")
            raise
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> List[QueryResult]:
        """
        Query the knowledge base using an embedding vector.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filters (e.g., {"source_url": "https://..."})
            where_document: Document content filters
            
        Returns:
            List of QueryResult objects, ranked by similarity
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "distances", "metadatas"]
            )
            
            # Parse results into QueryResult objects
            query_results = []
            
            if results and results["ids"]:
                for rank, (chunk_id, document, distance, metadata) in enumerate(
                    zip(
                        results["ids"][0],
                        results["documents"][0],
                        results["distances"][0],
                        results["metadatas"][0]
                    ),
                    start=1
                ):
                    query_results.append(QueryResult(
                        chunk_id=chunk_id,
                        content=document,
                        source_url=metadata.get("source_url", ""),
                        distance=distance,
                        metadata=metadata,
                        rank=rank
                    ))
            
            logger.info(f"Query returned {len(query_results)} results")
            return query_results
            
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "persist_directory": str(self.persist_directory),
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "total_chunks": 0,
                "error": str(e)
            }
    
    def delete_collection(self):
        """Delete the current collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
    
    def reset(self):
        """Reset the ChromaDB client (useful for testing)."""
        try:
            self.client.reset()
            logger.info("Reset ChromaDB client")
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB: {e}")
            raise
