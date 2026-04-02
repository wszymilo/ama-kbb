#!/usr/bin/env python
"""
Query CLI for retrieving chunks from ChromaDB knowledge base.

Usage:
    python rag_query.py --collection kb_poc --question "What are quantum error correction codes?"
    python rag_query.py -c kb_poc -q "surface codes" --top-k 10
    python rag_query.py --list-collections
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kbb.storage.chroma_store import ChromaKBStore
from kbb.schemas.models import QueryResult

# Try to import sentence_transformers for embedding generation
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QueryCLI:
    """Command-line interface for querying the knowledge base."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize query CLI.
        
        Args:
            persist_directory: ChromaDB persist directory
        """
        self.persist_directory = persist_directory
        self.embedding_model = None
        
        if HAS_EMBEDDINGS:
            # Initialize embedding model (same as used for building KB)
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
            logger.info("Embedding model loaded")
    
    def generate_query_embedding(self, question: str) -> List[float]:
        """
        Generate embedding for a query string.
        
        Args:
            question: Query text
            
        Returns:
            Embedding vector
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not available. Install sentence-transformers.")
        
        embedding = self.embedding_model.encode(question, convert_to_numpy=True)
        return embedding.tolist()
    
    def query(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
        verbose: bool = False
    ) -> List[QueryResult]:
        """
        Query the knowledge base.
        
        Args:
            collection_name: ChromaDB collection name
            question: Question to ask
            top_k: Number of results to return
            verbose: Whether to print detailed output
            
        Returns:
            List of QueryResult objects
        """
        # Initialize ChromaDB store
        store = ChromaKBStore(
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        
        # Get collection stats
        stats = store.get_collection_stats()
        logger.info(f"Querying collection: {collection_name}")
        logger.info(f"Total chunks in collection: {stats['total_chunks']}")
        
        if stats['total_chunks'] == 0:
            print(f"\nWarning: Collection '{collection_name}' is empty!")
            return []
        
        # Generate query embedding
        logger.info(f"Generating embedding for query: {question}")
        query_embedding = self.generate_query_embedding(question)
        
        # Query ChromaDB
        logger.info(f"Searching for top {top_k} results...")
        results = store.query(
            query_embedding=query_embedding,
            n_results=top_k
        )
        
        return results
    
    def list_collections(self):
        """List all available collections in ChromaDB."""
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collections = client.list_collections()
        
        print(f"\nAvailable collections in {self.persist_directory}:")
        print("=" * 80)
        
        if not collections:
            print("No collections found.")
        else:
            for col in collections:
                count = col.count()
                print(f"  - {col.name}: {count} chunks")
        
        print()
    
    def print_results(self, results: List[QueryResult], verbose: bool = False):
        """
        Print query results in a formatted way.
        
        Args:
            results: List of QueryResult objects
            verbose: Whether to print full content
        """
        if not results:
            print("\nNo results found.")
            return
        
        print(f"\nFound {len(results)} results:")
        print("=" * 80)
        
        for result in results:
            print(f"\n[Rank {result.rank}] (Distance: {result.distance:.4f})")
            print(f"Source: {result.source_url}")
            
            if verbose:
                print(f"\nContent:")
                print("-" * 80)
                print(result.content)
                print("-" * 80)
                
                if result.metadata:
                    print(f"\nMetadata:")
                    for key, value in result.metadata.items():
                        print(f"  {key}: {value}")
            else:
                # Print first 200 characters
                preview = result.content[:200].replace('\n', ' ')
                if len(result.content) > 200:
                    preview += "..."
                print(f"Preview: {preview}")
            
            print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Query the knowledge base built by AMA-KBB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a collection
  python rag_query.py --collection kb_poc --question "What is quantum error correction?"
  
  # Get more results
  python rag_query.py -c kb_poc -q "surface codes" --top-k 10
  
  # Verbose output with full content
  python rag_query.py -c kb_poc -q "topological codes" -v
  
  # List all collections
  python rag_query.py --list-collections
        """
    )
    
    parser.add_argument(
        "-c", "--collection",
        type=str,
        default="kb_poc",
        help="ChromaDB collection name (default: kb_poc)"
    )
    
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Question to ask the knowledge base"
    )
    
    parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show full content of results"
    )
    
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_db",
        help="ChromaDB persist directory (default: ./chroma_db)"
    )
    
    parser.add_argument(
        "--list-collections",
        action="store_true",
        help="List all available collections and exit"
    )
    
    args = parser.parse_args()
    
    # Check if sentence-transformers is available
    if not HAS_EMBEDDINGS and not args.list_collections:
        print("\nError: sentence-transformers is not installed.")
        print("Install it with: pip install sentence-transformers")
        print("\nOr add to requirements.txt: sentence-transformers>=2.2.0")
        sys.exit(1)
    
    # Initialize CLI
    cli = QueryCLI(persist_directory=args.persist_dir)
    
    # Handle list collections
    if args.list_collections:
        cli.list_collections()
        sys.exit(0)
    
    # Validate arguments
    if not args.question:
        parser.error("--question is required (unless using --list-collections)")
    
    try:
        # Query the knowledge base
        results = cli.query(
            collection_name=args.collection,
            question=args.question,
            top_k=args.top_k,
            verbose=args.verbose
        )
        
        # Print results
        cli.print_results(results, verbose=args.verbose)
        
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
