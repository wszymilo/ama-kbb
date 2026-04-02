#!/usr/bin/env python
"""
Test script for Issue #18 and #19 - Artifacts and Query CLI.

This script demonstrates:
1. Creating run artifacts
2. Saving pipeline outputs
3. Querying ChromaDB with the query CLI
"""

import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kbb.storage.artifact_store import ArtifactStore
from kbb.storage.chroma_store import ChromaKBStore
from kbb.schemas.models import (
    ResearchPlan,
    SourceCandidate,
    SourceReview,
    ScrapedDocument,
    CleanChunk,
    PipelineRunSummary,
)


def test_artifacts():
    """Test artifact storage (Issue #19)."""
    print("\n" + "="*80)
    print("Testing Artifact Storage (Issue #19)")
    print("="*80)
    
    # Initialize artifact store
    store = ArtifactStore(base_dir="./artifacts")
    
    # Create a test run
    run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\nCreating test run: {run_id}")
    
    run_dir = store.create_run_directory(run_id)
    print(f"Run directory created: {run_dir}")
    
    # 1. Save research plan
    print("\n1. Saving research plan...")
    plan = ResearchPlan(
        topic="quantum error correction",
        subtopics=["surface codes", "topological codes", "fault tolerance"],
        search_queries=[
            "quantum error correction basics",
            "surface code implementation",
            "topological quantum computing"
        ],
        scope="Focus on practical implementations and recent advances"
    )
    store.save_research_plan(run_id, plan)
    print("   ✓ Research plan saved")
    
    # 2. Save source candidates
    print("\n2. Saving source candidates...")
    candidates = [
        SourceCandidate(
            url="https://arxiv.org/abs/quant-ph/0504218",
            title="Surface codes: Towards practical large-scale quantum computation",
            description="Foundational paper on surface codes",
            source_type="paper"
        ),
        SourceCandidate(
            url="https://quantumcomputing.stackexchange.com/questions/tagged/error-correction",
            title="Quantum Error Correction Questions",
            description="Community Q&A on error correction",
            source_type="forum"
        ),
    ]
    store.save_source_candidates(run_id, candidates)
    print(f"   ✓ {len(candidates)} source candidates saved")
    
    # 3. Save source reviews
    print("\n3. Saving source reviews...")
    reviews = [
        SourceReview(
            source=candidates[0],
            approved=True,
            authority_score=5.0,
            relevance_score=5.0,
            reliability_score=5.0,
            recency_score=3.0,
            completeness_score=5.0,
            rationale="Foundational paper from leading researchers, highly cited"
        ),
        SourceReview(
            source=candidates[1],
            approved=False,
            authority_score=2.0,
            relevance_score=3.0,
            reliability_score=2.0,
            recency_score=4.0,
            completeness_score=2.0,
            rationale="Community forum with varying quality, not authoritative enough for knowledge base"
        ),
    ]
    store.save_source_reviews(run_id, reviews)
    print(f"   ✓ {len(reviews)} source reviews saved")
    
    # 4. Save scraped documents
    print("\n4. Saving scraped documents...")
    documents = [
        ScrapedDocument(
            source_url=candidates[0].url,
            title=candidates[0].title,
            content="Surface codes are a family of quantum error correcting codes...",
            word_count=150,
            status="success"
        )
    ]
    store.save_scraped_documents(run_id, documents)
    print(f"   ✓ {len(documents)} documents saved")
    
    # 5. Save chunks (with dummy embeddings)
    print("\n5. Saving chunks...")
    chunks = [
        CleanChunk(
            chunk_id=f"{run_id}_chunk_0",
            document_id=f"{run_id}_doc_0",
            source_url=candidates[0].url,
            content="Surface codes are a family of quantum error correcting codes...",
            chunk_index=0,
            word_count=150,
            metadata={"title": "Surface codes", "topic": "quantum error correction"},
            embedding=[0.1] * 768  # Dummy embedding vector
        )
    ]
    store.save_chunks(run_id, chunks)
    print(f"   ✓ {len(chunks)} chunks saved")
    
    # 6. Save run summary
    print("\n6. Saving run summary...")
    summary = PipelineRunSummary(
        run_id=run_id,
        topic="quantum error correction",
        collection_name="test_collection",
        sources_discovered=2,
        sources_approved=1,
        sources_rejected=1,
        documents_scraped=1,
        documents_failed=0,
        chunks_created=1,
        chunks_embedded=1,
        chunks_stored=1,
        artifacts_path=str(run_dir)
    )
    summary.mark_completed()
    store.save_run_summary(summary)
    print("   ✓ Run summary saved")
    
    # List all runs
    print("\n7. Listing all runs...")
    runs = store.list_runs()
    print(f"   Found {len(runs)} run(s):")
    for run in runs[:5]:  # Show last 5
        print(f"     - {run['run_id']}: {run['topic']} ({run['status']})")
    
    print(f"\n✓ Artifact storage test completed!")
    print(f"  Artifacts saved to: {run_dir}")
    return run_id, chunks


def test_chromadb_query(chunks):
    """Test ChromaDB storage and query (Issue #18)."""
    print("\n" + "="*80)
    print("Testing ChromaDB Storage and Query (Issue #18)")
    print("="*80)
    
    collection_name = "test_kb"
    
    # Initialize ChromaDB store
    print(f"\n1. Initializing ChromaDB with collection '{collection_name}'...")
    store = ChromaKBStore(
        persist_directory="./test_chroma_db",
        collection_name=collection_name
    )
    print("   ✓ ChromaDB initialized")
    
    # Add chunks
    print(f"\n2. Adding {len(chunks)} chunk(s) to ChromaDB...")
    count = store.add_chunks(chunks)
    print(f"   ✓ {count} chunk(s) added")
    
    # Get stats
    print("\n3. Getting collection stats...")
    stats = store.get_collection_stats()
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Total chunks: {stats['total_chunks']}")
    
    # Query
    print("\n4. Querying ChromaDB...")
    print("   (Using dummy query embedding)")
    query_embedding = [0.1] * 768  # Dummy query vector
    results = store.query(query_embedding=query_embedding, n_results=5)
    
    print(f"\n   Found {len(results)} result(s):")
    for result in results:
        print(f"     [Rank {result.rank}] Distance: {result.distance:.4f}")
        print(f"     Source: {result.source_url}")
        print(f"     Preview: {result.content[:80]}...")
        print()
    
    print("✓ ChromaDB storage and query test completed!")
    print(f"  ChromaDB location: ./test_chroma_db")
    print(f"  Collection: {collection_name}")
    
    return collection_name


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AMA-KBB: Testing Issue #18 and #19")
    print("="*80)
    print("\nThis script demonstrates:")
    print("  - Issue #19: Saving run artifacts and summaries")
    print("  - Issue #18: ChromaDB storage and query functionality")
    
    try:
        # Test artifacts
        run_id, chunks = test_artifacts()
        
        # Test ChromaDB
        collection_name = test_chromadb_query(chunks)
        
        # Final summary
        print("\n" + "="*80)
        print("All Tests Passed!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Review artifacts in: ./artifacts/")
        print(f"  2. Test query CLI: python rag_query.py --collection {collection_name} --question 'quantum error' --persist-dir ./test_chroma_db")
        print("  3. List collections: python rag_query.py --list-collections --persist-dir ./test_chroma_db")
        print("\nNote: For real queries, you need sentence-transformers installed:")
        print("  pip install sentence-transformers")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
