"""
Artifact storage for saving pipeline run outputs for debugging and demo.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict

from ..schemas.models import (
    ResearchPlan,
    SourceCandidate,
    SourceReview,
    ScrapedDocument,
    CleanChunk,
    PipelineRunSummary,
)

logger = logging.getLogger(__name__)


class ArtifactStore:
    """
    Store and manage pipeline artifacts for debugging and demo purposes.
    """
    
    def __init__(self, base_dir: str = "./artifacts"):
        """
        Initialize artifact store.
        
        Args:
            base_dir: Base directory for all artifacts
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized artifact store at {self.base_dir}")
    
    def create_run_directory(self, run_id: str) -> Path:
        """
        Create a directory for a specific run.
        
        Args:
            run_id: Unique run identifier
            
        Returns:
            Path to the run directory
        """
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (run_dir / "research").mkdir(exist_ok=True)
        (run_dir / "sources").mkdir(exist_ok=True)
        (run_dir / "documents").mkdir(exist_ok=True)
        (run_dir / "chunks").mkdir(exist_ok=True)
        
        logger.info(f"Created run directory: {run_dir}")
        return run_dir
    
    def save_research_plan(self, run_id: str, plan: ResearchPlan) -> Path:
        """Save research plan to artifacts."""
        run_dir = self.base_dir / run_id / "research"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = run_dir / f"research_plan_v{plan.version}.json"
        with open(filepath, "w") as f:
            f.write(plan.model_dump_json(indent=2))
        
        logger.info(f"Saved research plan to {filepath}")
        return filepath
    
    def save_source_candidates(self, run_id: str, candidates: List[SourceCandidate]) -> Path:
        """Save discovered source candidates."""
        run_dir = self.base_dir / run_id / "sources"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = run_dir / "source_candidates.json"
        data = [candidate.model_dump() for candidate in candidates]
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved {len(candidates)} source candidates to {filepath}")
        return filepath
    
    def save_source_reviews(self, run_id: str, reviews: List[SourceReview]) -> Path:
        """Save SME source reviews."""
        run_dir = self.base_dir / run_id / "sources"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = run_dir / "source_reviews.json"
        data = [review.model_dump() for review in reviews]
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        # Also save summary statistics
        approved = sum(1 for r in reviews if r.approved)
        rejected = len(reviews) - approved
        
        summary_path = run_dir / "review_summary.txt"
        with open(summary_path, "w") as f:
            f.write(f"Source Review Summary\n")
            f.write(f"====================\n\n")
            f.write(f"Total sources reviewed: {len(reviews)}\n")
            f.write(f"Approved: {approved}\n")
            f.write(f"Rejected: {rejected}\n\n")
            f.write(f"Approved Sources:\n")
            for review in reviews:
                if review.approved:
                    f.write(f"  - {review.source.url}\n")
                    f.write(f"    Title: {review.source.title}\n")
                    f.write(f"    Rationale: {review.rationale}\n\n")
            
            f.write(f"\nRejected Sources:\n")
            for review in reviews:
                if not review.approved:
                    f.write(f"  - {review.source.url}\n")
                    f.write(f"    Title: {review.source.title}\n")
                    f.write(f"    Rationale: {review.rationale}\n\n")
        
        logger.info(f"Saved {len(reviews)} source reviews to {filepath}")
        return filepath
    
    def save_scraped_documents(self, run_id: str, documents: List[ScrapedDocument]) -> Path:
        """Save scraped documents."""
        run_dir = self.base_dir / run_id / "documents"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        filepath = run_dir / "scraped_documents_metadata.json"
        metadata = []
        
        for i, doc in enumerate(documents):
            # Save document content separately
            doc_filename = f"document_{i:04d}.txt"
            doc_path = run_dir / doc_filename
            
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(f"Source: {doc.source_url}\n")
                f.write(f"Title: {doc.title}\n")
                f.write(f"Scraped: {doc.scraped_at}\n")
                f.write(f"Status: {doc.status}\n")
                f.write(f"{'='*80}\n\n")
                f.write(doc.content)
            
            # Collect metadata
            meta = doc.model_dump()
            meta["content"] = f"[See {doc_filename}]"
            metadata.append(meta)
        
        with open(filepath, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Saved {len(documents)} scraped documents to {run_dir}")
        return filepath
    
    def save_chunks(self, run_id: str, chunks: List[CleanChunk]) -> Path:
        """Save cleaned chunks."""
        run_dir = self.base_dir / run_id / "chunks"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chunk metadata (without embeddings for readability)
        filepath = run_dir / "chunks_metadata.json"
        metadata = []
        
        for chunk in chunks:
            chunk_dict = chunk.model_dump()
            # Remove embedding vector from JSON (too large)
            if "embedding" in chunk_dict and chunk_dict["embedding"]:
                chunk_dict["embedding"] = f"[Vector of length {len(chunk_dict['embedding'])}]"
            metadata.append(chunk_dict)
        
        with open(filepath, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Save full chunks with embeddings (for potential reuse)
        full_filepath = run_dir / "chunks_full.json"
        with open(full_filepath, "w") as f:
            json.dump([chunk.model_dump() for chunk in chunks], f, default=str)
        
        logger.info(f"Saved {len(chunks)} chunks to {run_dir}")
        return filepath
    
    def save_run_summary(self, summary: PipelineRunSummary) -> Path:
        """
        Save the final pipeline run summary.
        
        Args:
            summary: PipelineRunSummary object
            
        Returns:
            Path to the saved summary file
        """
        run_dir = self.base_dir / summary.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON summary
        json_path = run_dir / "run_summary.json"
        with open(json_path, "w") as f:
            f.write(summary.model_dump_json(indent=2))
        
        # Save human-readable summary
        txt_path = run_dir / "run_summary.txt"
        with open(txt_path, "w") as f:
            f.write(f"Pipeline Run Summary\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Run ID: {summary.run_id}\n")
            f.write(f"Topic: {summary.topic}\n")
            f.write(f"Collection: {summary.collection_name}\n")
            f.write(f"Status: {summary.status}\n\n")
            
            f.write(f"Timing:\n")
            f.write(f"  Started: {summary.started_at}\n")
            if summary.completed_at:
                f.write(f"  Completed: {summary.completed_at}\n")
                f.write(f"  Duration: {summary.duration_seconds:.2f} seconds\n\n")
            
            f.write(f"Source Statistics:\n")
            f.write(f"  Discovered: {summary.sources_discovered}\n")
            f.write(f"  Approved: {summary.sources_approved}\n")
            f.write(f"  Rejected: {summary.sources_rejected}\n\n")
            
            f.write(f"Document Statistics:\n")
            f.write(f"  Successfully scraped: {summary.documents_scraped}\n")
            f.write(f"  Failed to scrape: {summary.documents_failed}\n\n")
            
            f.write(f"Chunk Statistics:\n")
            f.write(f"  Created: {summary.chunks_created}\n")
            f.write(f"  Embedded: {summary.chunks_embedded}\n")
            f.write(f"  Stored in ChromaDB: {summary.chunks_stored}\n\n")
            
            if summary.error_message:
                f.write(f"Error:\n")
                f.write(f"  {summary.error_message}\n\n")
            
            if summary.artifacts_path:
                f.write(f"Artifacts saved to: {summary.artifacts_path}\n")
        
        logger.info(f"Saved run summary to {run_dir}")
        return txt_path
    
    def get_run_summary(self, run_id: str) -> Optional[PipelineRunSummary]:
        """
        Load a run summary from artifacts.
        
        Args:
            run_id: Run identifier
            
        Returns:
            PipelineRunSummary object if found, None otherwise
        """
        summary_path = self.base_dir / run_id / "run_summary.json"
        
        if not summary_path.exists():
            logger.warning(f"No summary found for run {run_id}")
            return None
        
        with open(summary_path, "r") as f:
            data = json.load(f)
            return PipelineRunSummary(**data)
    
    def list_runs(self) -> List[Dict[str, Any]]:
        """
        List all pipeline runs with basic info.
        
        Returns:
            List of run information dictionaries
        """
        runs = []
        
        for run_dir in self.base_dir.iterdir():
            if run_dir.is_dir():
                summary_path = run_dir / "run_summary.json"
                if summary_path.exists():
                    with open(summary_path, "r") as f:
                        summary_data = json.load(f)
                        runs.append({
                            "run_id": summary_data.get("run_id"),
                            "topic": summary_data.get("topic"),
                            "status": summary_data.get("status"),
                            "started_at": summary_data.get("started_at"),
                            "completed_at": summary_data.get("completed_at"),
                        })
        
        # Sort by start time (most recent first)
        runs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        return runs
