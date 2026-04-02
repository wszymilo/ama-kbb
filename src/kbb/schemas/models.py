"""
Pydantic models for typed handoffs between agents and pipeline artifacts.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """Research plan created by Researcher agent."""
    topic: str = Field(..., description="Main research topic")
    subtopics: List[str] = Field(default_factory=list, description="List of subtopics to research")
    search_queries: List[str] = Field(default_factory=list, description="Proposed search queries")
    scope: str = Field(default="", description="Scope and boundaries of the research")
    created_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Plan version number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "quantum error correction",
                "subtopics": ["surface codes", "topological codes", "fault tolerance"],
                "search_queries": ["quantum error correction basics", "surface code implementation"],
                "scope": "Focus on practical implementations and recent advances",
                "version": 1
            }
        }


class SourceCandidate(BaseModel):
    """Candidate source discovered during research."""
    url: str = Field(..., description="Source URL")
    title: str = Field(default="", description="Source title")
    description: str = Field(default="", description="Brief description or snippet")
    source_type: str = Field(default="webpage", description="Type of source (webpage, paper, documentation, etc.)")
    discovered_at: datetime = Field(default_factory=datetime.now)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score if available")


class SourceReview(BaseModel):
    """SME review of a source candidate."""
    source: SourceCandidate = Field(..., description="The source being reviewed")
    approved: bool = Field(..., description="Whether the source is approved")
    authority_score: float = Field(..., ge=0.0, le=5.0, description="Authority rating (0-5)")
    relevance_score: float = Field(..., ge=0.0, le=5.0, description="Relevance rating (0-5)")
    reliability_score: float = Field(..., ge=0.0, le=5.0, description="Reliability rating (0-5)")
    recency_score: float = Field(..., ge=0.0, le=5.0, description="Recency rating (0-5)")
    completeness_score: float = Field(..., ge=0.0, le=5.0, description="Completeness rating (0-5)")
    rationale: str = Field(default="", description="Explanation for approval/rejection")
    reviewed_at: datetime = Field(default_factory=datetime.now)
    reviewer: str = Field(default="SME", description="Name/ID of the reviewing agent")


class ScrapedDocument(BaseModel):
    """Document fetched by Scraper agent."""
    source_url: str = Field(..., description="Original source URL")
    title: str = Field(default="", description="Document title")
    content: str = Field(..., description="Raw scraped content")
    content_type: str = Field(default="text/html", description="Content MIME type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    scraped_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="success", description="Scraping status")
    error_message: Optional[str] = Field(None, description="Error message if scraping failed")
    word_count: int = Field(default=0, description="Word count of content")


class CleanChunk(BaseModel):
    """Cleaned and chunked document ready for embedding."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    source_url: str = Field(..., description="Original source URL")
    content: str = Field(..., description="Cleaned chunk content")
    chunk_index: int = Field(..., ge=0, description="Position in document (0-indexed)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata (title, topic, etc.)")
    word_count: int = Field(default=0, description="Word count")
    created_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = Field(None, description="Embedding vector if generated")


class PipelineRunSummary(BaseModel):
    """Summary of a complete pipeline run."""
    run_id: str = Field(..., description="Unique run identifier")
    topic: str = Field(..., description="Research topic")
    rubric_path: Optional[str] = Field(None, description="Path to rubric file used")
    collection_name: str = Field(..., description="ChromaDB collection name")
    
    # Counts and statistics
    sources_discovered: int = Field(default=0, description="Number of candidate sources found")
    sources_approved: int = Field(default=0, description="Number of sources approved by SME")
    sources_rejected: int = Field(default=0, description="Number of sources rejected by SME")
    documents_scraped: int = Field(default=0, description="Number of documents successfully scraped")
    documents_failed: int = Field(default=0, description="Number of documents that failed to scrape")
    chunks_created: int = Field(default=0, description="Number of chunks created")
    chunks_embedded: int = Field(default=0, description="Number of chunks successfully embedded")
    chunks_stored: int = Field(default=0, description="Number of chunks stored in ChromaDB")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)
    duration_seconds: Optional[float] = Field(None, description="Total run duration")
    
    # Status
    status: str = Field(default="running", description="Run status: running, completed, failed, partial")
    error_message: Optional[str] = Field(None, description="Error message if run failed")
    
    # Artifacts
    artifacts_path: Optional[str] = Field(None, description="Path to artifacts directory")
    
    def mark_completed(self):
        """Mark the run as completed and calculate duration."""
        self.completed_at = datetime.now()
        self.status = "completed"
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def mark_failed(self, error: str):
        """Mark the run as failed with error message."""
        self.completed_at = datetime.now()
        self.status = "failed"
        self.error_message = error
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.completed_at).total_seconds()


class QueryResult(BaseModel):
    """Result from querying the knowledge base."""
    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Chunk content")
    source_url: str = Field(..., description="Original source URL")
    distance: float = Field(..., description="Distance/similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Associated metadata")
    rank: int = Field(..., ge=1, description="Result rank (1-based)")
