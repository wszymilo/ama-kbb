"""State class for Kbb Flow."""

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from kbb.schemas.models import ResearchPlan, PlanReview


class KbbState(BaseModel):
    """State for Kbb Flow with revision tracking."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    current_year: str = "2026"
    rubric_path: str = ""
    revision_attempts: int = 0
    max_revisions: int = 2
    current_plan: Optional[ResearchPlan] = None
    current_review: Optional[PlanReview] = None
    human_approved: bool = False
    workflow_aborted: bool = False
