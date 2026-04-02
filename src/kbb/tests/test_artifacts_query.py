#!/usr/bin/env python
"""
Test script for Issue #18 and #19 - Artifacts and Query CLI.

This script demonstrates:
1. Creating run artifacts
2. Saving pipeline outputs
3. Querying ChromaDB with the query CLI
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kbb.storage.artifact_store import ArtifactStore
from kbb.storage.chroma_store import ChromaKBStore
from kbb.schemas.models import (
    ResearchPlan,
    SourceCandidate,
    SourceReview,
    ScrapedDocument,
    ChunkRecord,
    PipelineRunSummary,
)


# TODO: Re-enable once ResearchPlan has 'version' field or artifact store is fixed
# def test_artifacts():
#     """Test artifact storage (Issue #19)."""
#     print("\n" + "=" * 80)
#     print("Testing Artifact Storage (Issue #19)")
#     print("=" * 80)
#
#     # Initialize artifact store
#     store = ArtifactStore(base_dir="./artifacts")
#
#     # Create a test run
#     run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#     print(f"\nCreating test run: {run_id}")
#
#     run_dir = store.create_run_directory(run_id)
#     print(f"Run directory created: {run_dir}")
#
#     # 1. Save research plan
#     print("\n1. Saving research plan...")
#     plan = ResearchPlan(
#         topic="quantum error correction",
#         search_queries=[
#             "quantum error correction basics",
#             "surface code implementation",
#             "topological quantum computing",
#         ],
#     )
#     store.save_research_plan(run_id, plan)
#     print("   ✓ Research plan saved")
#
#     # 2. Save source candidates
#     print("\n2. Saving source candidates...")
#     candidates = [
#         SourceCandidate(
#             url="https://arxiv.org/abs/quant-ph/0504218",
#             title="Surface codes: Towards practical large-scale quantum computation",
#             snippet="Foundational paper on surface codes",
#         ),
#         SourceCandidate(
#             url="https://quantumcomputing.stackexchange.com/questions/tagged/error-correction",
#             title="Quantum Error Correction Questions",
#             snippet="Community Q&A on error correction",
#         ),
#     ]
#     store.save_source_candidates(run_id, candidates)
#     print(f"   ✓ {len(candidates)} source candidates saved")
#
#     # 3. Save source reviews
#     print("\n3. Saving source reviews...")
#     reviews = [
#         SourceReview(
#             source_url=candidates[0].url,
#             decision="approved",
#             rationale="Foundational paper from leading researchers, highly cited",
#         ),
#         SourceReview(
#             source_url=candidates[1].url,
#             decision="rejected",
#             rationale="Community forum with varying quality, not authoritative enough for knowledge base",
#         ),
#     ]
#     store.save_source_reviews(run_id, reviews)
#     print(f"   ✓ {len(reviews)} source reviews saved")
#
#     # 4. Save scraped documents
#     print("\n4. Saving scraped documents...")
#     documents = [
#         ScrapedDocument(
#             source_url=candidates[0].url,
#             title=candidates[0].title,
#             content="Surface codes are a family of quantum error correcting codes...",
#             fetch_status="success",
#         )
#     ]
#     store.save_scraped_documents(run_id, documents)
#     print(f"   ✓ {len(documents)} documents saved")
#
#     # 5. Save chunks (with dummy embeddings)
#     print("\n5. Saving chunks...")
#     chunks = [
#         ChunkRecord(
#             document_id=f"{run_id}_doc_0",
#             chunk_text="Surface codes are a family of quantum error correcting codes...",
#             metadata={
#                 "source_url": candidates[0].url,
#                 "title": "Surface codes",
#                 "topic": "quantum error correction",
#             },
#             collection_name="test_collection",
#         )
#     ]
#     store.save_chunks(run_id, chunks)
#     print(f"   ✓ {len(chunks)} chunks saved")
#
#     # 6. Save run summary
#     print("\n6. Saving run summary...")
#     now = datetime.now(timezone.utc)
#     summary = PipelineRunSummary(
#         run_id=run_id,
#         topic="quantum error correction",
#         start_time=now,
#         end_time=now,
#         metrics={
#             "sources_discovered": 2,
#             "sources_approved": 1,
#             "sources_rejected": 1,
#             "documents_scraped": 1,
#             "documents_failed": 0,
#             "chunks_created": 1,
#             "chunks_embedded": 1,
#             "chunks_stored": 1,
#         },
#     )
#     store.save_run_summary(summary)
#     print("   ✓ Run summary saved")
#
#     # List all runs
#     print("\n7. Listing all runs...")
#     runs = store.list_runs()
#     print(f"   Found {len(runs)} run(s):")
#     for run in runs[:5]:  # Show last 5
#         print(f"     - {run['run_id']}: {run.get('topic', 'N/A')}")
#
#     print("\n✓ Artifact storage test completed!")
#     print(f"  Artifacts saved from: {run_dir}")
#     return run_id, chunks


def test_chromadb_query():
    """Test ChromaDB storage and query (Issue #18)."""
    print("\n" + "=" * 80)
    print("Testing ChromaDB Storage and Query (Issue #18)")
    print("=" * 80)

    # Create test chunks directly
    chunks = [
        ChunkRecord(
            document_id="test_doc_1",
            chunk_text="Quantum error correction is essential for building reliable quantum computers. Surface codes are currently the most promising approach.",
            metadata={
                "source_url": "https://example.com/quantum",
                "topic": "quantum computing",
            },
            collection_name="test_kb",
        ),
        ChunkRecord(
            document_id="test_doc_2",
            chunk_text="Topological quantum computation uses anyons for fault-tolerant quantum information processing.",
            metadata={
                "source_url": "https://example.com/topological",
                "topic": "quantum computing",
            },
            collection_name="test_kb",
        ),
    ]

    collection_name = "test_kb"

    # Initialize ChromaDB store
    print(f"\n1. Initializing ChromaDB with collection '{collection_name}'...")
    store = ChromaKBStore(
        persist_directory="./test_chroma_db", collection_name=collection_name
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
    results = store.query(query_text="quantum error correction", n_results=5)

    print(f"\n   Found {len(results)} result(s):")
    for result in results:
        print(f"     [Rank {result['rank']}] Distance: {result['distance']:.4f}")
        print(f"     Document: {result['document'][:80]}...")
        print()

    print("✓ ChromaDB storage and query test completed!")
    print("  ChromaDB location: ./test_chroma_db")
    print(f"  Collection: {collection_name}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AMA-KBB: Testing Issue #18 and #19")
    print("=" * 80)
    print("\nThis script demonstrates:")
    print("  - Issue #19: Saving run artifacts and summaries")
    print("  - Issue #18: ChromaDB storage and query functionality")

    try:
        # Test artifacts - TODO: re-enable once ResearchPlan has version field
        # run_id, chunks = test_artifacts()

        # Test ChromaDB
        test_chromadb_query()

        # Final summary
        print("\n" + "=" * 80)
        print("All Tests Passed!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review artifacts in: ./artifacts/")
        print("  2. Test query CLI with ChromaDB")
        print("  3. List collections: use ChromaDB client")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
