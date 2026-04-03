from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchPlan(BaseModel):
    """A plan outlining how to research a given topic."""

    topic: str = Field(..., description="The main research topic")
    objectives: List[str] = Field(
        default_factory=list,
        description="List of research objectives for this topic",
    )
    subtopics: List[str] = Field(
        default_factory=list,
        description="List of subtopics to explore",
    )
    search_queries: List[str] = Field(
        default_factory=list, description="List of search queries to explore"
    )
    source_expectations: str = Field(
        default="",
        description="Expected source types and quality criteria",
    )
    created_at: datetime = Field(
        default_factory=_utc_now, description="Timestamp of plan creation"
    )


class SourceCandidate(BaseModel):
    """A potential source discovered during research."""

    url: str = Field(..., description="URL of the candidate source")
    title: Optional[str] = Field(None, description="Title of the source, if known")
    snippet: Optional[str] = Field(
        None, description="Short excerpt or description of the source"
    )


class SourceReview(BaseModel):
    """Review outcome for a candidate source after SME validation."""

    source_url: str = Field(..., description="URL of the reviewed source")
    title: Optional[str] = Field(None, description="Title of the source for context")
    decision: str = Field(
        ..., description="Review decision, e.g., 'approved' or 'rejected'"
    )
    rationale: str = Field(..., description="Explicit explanation for the decision")
    rubric_criteria_considered: List[str] = Field(
        default_factory=list,
        description="List of rubric criteria considered in the review",
    )
    reviewed_at: datetime = Field(
        default_factory=_utc_now, description="When the review was performed"
    )


class PlanReview(BaseModel):
    """Review outcome for a research plan after SME validation."""

    decision: str = Field(
        ..., description="Review decision: 'approved' or 'revision_requested'"
    )
    rationale: str = Field(..., description="Explicit explanation for the decision")
    concerns: List[str] = Field(
        default_factory=list,
        description="Specific issues to address if revision requested",
    )
    reviewed_at: datetime = Field(
        default_factory=_utc_now, description="When the review was performed"
    )


class ScrapedDocument(BaseModel):
    """Result of fetching the content of an approved source."""

    source_url: str = Field(..., description="URL of the source that was fetched")
    title: Optional[str] = Field(
        None, description="Title of the document, if extracted"
    )
    fetch_status: str = Field(
        ..., description="Status of the fetch operation, e.g., 'success' or 'failed'"
    )
    content: str = Field(
        ..., description="Raw textual content retrieved from the source"
    )
    fetched_at: datetime = Field(
        default_factory=_utc_now, description="When the fetch occurred"
    )


class CleanDocument(BaseModel):
    """Document after cleaning and normalisation steps."""

    status: str = Field(
        ...,
        description="Document status: 'cleaned' or 'filtered'",
    )
    source_url: str = Field(..., description="Original source URL")
    title: Optional[str] = Field(None, description="Document title")
    document_id: Optional[str] = Field(
        None,
        description="Unique identifier for the document (slugified URL or generated)",
    )
    cleaned_text: str = Field(..., description="Sanitized and cleaned document text")
    filter_reason: Optional[str] = Field(
        None, description="Reason for filtering if status='filtered'"
    )
    cleaned_at: datetime = Field(
        default_factory=_utc_now, description="When cleaning was performed"
    )


class ChunkRecord(BaseModel):
    """A chunk of text ready for embedding and storage."""

    document_id: str = Field(..., description="Identifier of the source document")
    chunk_text: str = Field(..., description="Text of the chunk")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata about the chunk"
    )
    collection_name: str = Field(
        ..., description="Name of the ChromaDB collection the chunk belongs to"
    )
    chunked_at: datetime = Field(
        default_factory=_utc_now, description="Timestamp of chunk creation"
    )


class PipelineRunSummary(BaseModel):
    """Summary of a full pipeline execution run."""

    run_id: str = Field(..., description="Unique identifier for the pipeline run")
    topic: str = Field(..., description="Research topic for this run")
    start_time: datetime = Field(..., description="When the pipeline started")
    end_time: datetime = Field(..., description="When the pipeline finished")
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key‑value metrics collected during the run (e.g., number of sources, chunks, etc.)",
    )
