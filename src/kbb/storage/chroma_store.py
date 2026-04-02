"""
ChromaDB storage interface for knowledge base chunks.
Uses nomic-embed-text-v1.5 with proper search/index prefixes.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from kbb.config import get_config
from kbb.schemas.models import ChunkRecord

SEARCH_DOCUMENT_PREFIX = "search_document: "
SEARCH_QUERY_PREFIX = "search_query: "

logger = logging.getLogger(__name__)


class ChromaKBStore:
    """
    Interface for storing and querying knowledge base chunks in ChromaDB.
    Uses nomic-embed-text-v1.5 embedding function with proper prefixes.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """
        Initialize ChromaDB storage with nomic embedder.

        Args:
            persist_directory: Directory to persist ChromaDB data.
                                Defaults to config.CHROMA_DIR.
            collection_name: Name of the collection to use.
                              Defaults to config.COLLECTION_NAME.
        """
        config = get_config()

        self.persist_directory = Path(persist_directory or config.CHROMA_DIR)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name or config.COLLECTION_NAME

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize nomic embedding function
        # Note: ChromaDB will handle prefixes automatically when we pass documents
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=config.EMBEDDING_MODEL, trust_remote_code=True
            )
        )

        # Get or create collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,  # type: ignore[arg-type]
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            f"Initialized ChromaDB store at {self.persist_directory} with collection '{self.collection_name}' using {config.EMBEDDING_MODEL}"
        )

    def add_chunks(self, chunks: List[ChunkRecord]) -> int:
        """
        Add chunks to the ChromaDB collection.
        ChromaDB will compute embeddings on-the-fly using nomic embedder with 'search_document:' prefix.

        Args:
            chunks: List of ChunkRecord objects.

        Returns:
            Number of chunks successfully added
        """
        if not chunks:
            logger.warning("No chunks to add")
            return 0

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = chunk.document_id
            text = chunk.chunk_text

            if not chunk_id or not text:
                logger.warning(f"Chunk missing id or text, skipping: {chunk}")
                continue

            metadata = {
                **chunk.metadata,
                "collection_name": chunk.collection_name,
                "chunked_at": chunk.chunked_at.isoformat()
                if chunk.chunked_at
                else None,
            }

            ids.append(chunk_id)
            documents.append(f"{SEARCH_DOCUMENT_PREFIX}{text}")
            metadatas.append(metadata)

        if not ids:
            logger.warning("No valid chunks to add")
            return 0

        # Add to ChromaDB (embeddings computed automatically)
        try:
            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)  # type: ignore[arg-type]
            logger.info(
                f"Successfully added {len(ids)} chunks to collection '{self.collection_name}'"
            )
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {e}")
            raise

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base using natural language.
        ChromaDB will compute query embedding on-the-fly using 'search_query:' prefix.

        Args:
            query_text: Natural language query
            n_results: Number of results to return
            where: Metadata filters (e.g., {"source_url": "https://..."})
            where_document: Document content filters

        Returns:
            List of result dictionaries with keys: id, document, distance, metadata, rank
        """
        try:
            prefixed_query = f"{SEARCH_QUERY_PREFIX}{query_text}"

            results = self.collection.query(
                query_texts=[prefixed_query],
                n_results=n_results,
                where=where,
                where_document=where_document,  # type: ignore[arg-type]
                include=["documents", "distances", "metadatas"],
            )

            # Parse results into simple dictionaries
            query_results = []

            if results and results["ids"]:
                for rank, (chunk_id, document, distance, metadata) in enumerate(
                    zip(
                        results["ids"][0],
                        results["documents"][0],  # type: ignore[index]
                        results["distances"][0],  # type: ignore[index]
                        results["metadatas"][0],  # type: ignore[index]
                    ),
                    start=1,
                ):
                    # Remove the prefix from returned documents for display
                    clean_document = document.replace(SEARCH_DOCUMENT_PREFIX, "", 1)

                    query_results.append(
                        {
                            "id": chunk_id,
                            "document": clean_document,
                            "distance": distance,
                            "metadata": metadata,
                            "rank": rank,
                        }
                    )

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
                "error": str(e),
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
