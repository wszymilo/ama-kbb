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
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kbb.storage.chroma_store import ChromaKBStore

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
    
    def query(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.
        
        Args:
            collection_name: ChromaDB collection name
            question: Question to ask
            top_k: Number of results to return
            verbose: Whether to print detailed output
            
        Returns:
            List of result dictionaries
        """
        # Initialize ChromaDB store (it handles embeddings internally)
        store = ChromaKBStore(
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        
        # Get collection stats
        stats = store.get_collection_stats()
        logger.info(f"Querying collection: {collection_name}")
        logger.info(f"Total chunks: {stats.get('total_chunks', 0)}")
        
        if stats.get('total_chunks', 0) == 0:
            print(f"\nCollection '{collection_name}' is empty or doesn't exist.")
            return []
        
        # Query the store (ChromaDB handles embedding generation with proper prefix)
        results = store.query(query_text=question, n_results=top_k)
        
        # Display results
        print(f"\n{'='*80}")
        print(f"Query: {question}")
        print(f"Collection: {collection_name}")
        print(f"Results: {len(results)}/{top_k}")
        print(f"{'='*80}\n")
        
        for result in results:
            rank = result['rank']
            chunk_id = result['id']
            content = result['document']
            distance = result['distance']
            metadata = result['metadata']
            
            print(f"[{rank}] Chunk ID: {chunk_id}")
            print(f"    Distance: {distance:.4f}")
            print(f"    Source: {metadata.get('source_url', 'N/A')}")
            
            if verbose:
                print(f"    Content:\n{content}\n")
            else:
                # Preview first 200 chars
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"    Preview: {preview}\n")
        
        return results
    
    def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collections = client.list_collections()
        
        print(f"\n{'='*80}")
        print(f"ChromaDB Collections (persist_dir: {self.persist_directory})")
        print(f"{'='*80}\n")
        
        if not collections:
            print("No collections found.\n")
            return []
        
        collection_names = []
        for coll in collections:
            count = coll.count()
            collection_names.append(coll.name)
            print(f"  - {coll.name} ({count} chunks)")
        
        print()
        return collection_names


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Query ChromaDB knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a collection
  python rag_query.py -c kb_poc -q "What is quantum error correction?"
  
  # Get more results with verbose output
  python rag_query.py -c kb_poc -q "surface codes" --top-k 10 -v
  
  # List all collections
  python rag_query.py --list-collections
  
  # Use custom ChromaDB directory
  python rag_query.py -c kb_poc -q "error rates" --persist-dir ./my_chroma_db
        """
    )
    
    parser.add_argument(
        '-c', '--collection',
        type=str,
        help='ChromaDB collection name'
    )
    
    parser.add_argument(
        '-q', '--question',
        type=str,
        help='Question to ask the knowledge base'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show full content of chunks (default: preview only)'
    )
    
    parser.add_argument(
        '--persist-dir',
        type=str,
        default='./chroma_db',
        help='ChromaDB persist directory (default: ./chroma_db)'
    )
    
    parser.add_argument(
        '--list-collections',
        action='store_true',
        help='List all available collections'
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = QueryCLI(persist_directory=args.persist_dir)
    
    # Handle list collections
    if args.list_collections:
        cli.list_collections()
        return 0
    
    # Validate query arguments
    if not args.collection or not args.question:
        parser.error("--collection and --question are required (unless using --list-collections)")
        return 1
    
    # Execute query
    try:
        results = cli.query(
            collection_name=args.collection,
            question=args.question,
            top_k=args.top_k,
            verbose=args.verbose
        )
        
        if results:
            print(f"✓ Query completed successfully")
            return 0
        else:
            print(f"✗ No results found")
            return 1
            
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
