"""Simple Kbb workflow runner with revision loop."""

import json
from typing import Optional

import yaml
from crewai import Agent, Task

from kbb.tools.search import search
from kbb.tools.rubric_loader import get_rubric_loader
from kbb.schemas.models import ResearchPlan, PlanReview, ScrapedDocument


class KbbWorkflow:
    """Kbb workflow with automatic revision loop and human decision point."""

    def __init__(self, rubric_path: str = ""):
        self.rubric_path = rubric_path
        self.rubric = {}
        if rubric_path:
            loader = get_rubric_loader()
            self.rubric = loader.load_from_path(rubric_path)

        self._agents_config = self._load_yaml("src/kbb/config/agents.yaml")
        self._tasks_config = self._load_yaml("src/kbb/config/tasks.yaml")

        self.revision_attempts = 0
        self.max_revisions = 2
        self.topic = ""
        self.current_year = "2026"
        self.current_plan: Optional[ResearchPlan] = None
        self.current_review: Optional[PlanReview] = None
        self.scapered_docs: list[ScrapedDocument] = []
        self.human_approved = False
        self.workflow_aborted = False

    def _load_yaml(self, path: str) -> dict:
        """Load YAML configuration file."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _get_rubric_context(self) -> str:
        """Get rubric context for tasks."""
        if not self.rubric:
            return ""
        loader = get_rubric_loader()
        return f"\n\nRubric for review:\n{loader.get_rubric_summary(self.rubric)}"

    def _create_researcher_agent(self) -> Agent:
        """Create researcher agent."""
        config = self._agents_config.get("researcher", {})
        role = config.get("role", "").replace("{topic}", self.topic)
        goal = config.get("goal", "").replace("{topic}", self.topic)
        backstory = config.get("backstory", "").replace("{topic}", self.topic)
        llm = config.get("llm", "gpt-4o-mini")

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            tools=[search],
            verbose=True,
        )

    def _create_plan_reviewer_agent(self) -> Agent:
        """Create plan reviewer agent."""
        config = self._agents_config.get("plan_reviewer", {})
        role = config.get("role", "").replace("{topic}", self.topic)
        goal = config.get("goal", "").replace("{topic}", self.topic)
        backstory = config.get("backstory", "").replace("{topic}", self.topic)
        llm = config.get("llm", "gpt-4o-mini")

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
        )

    def _create_source_reviewer_agent(self) -> Agent:
        """Create source reviewer agent."""
        config = self._agents_config.get("source_reviewer", {})
        role = config.get("role", "").replace("{topic}", self.topic)
        goal = config.get("goal", "").replace("{topic}", self.topic)
        backstory = config.get("backstory", "").replace("{topic}", self.topic)
        llm = config.get("llm", "gpt-4o-mini")

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
        )

    def _create_reporting_agent(self) -> Agent:
        """Create reporting analyst agent."""
        config = self._agents_config.get("reporting_analyst", {})
        role = config.get("role", "").replace("{topic}", self.topic)
        goal = config.get("goal", "").replace("{topic}", self.topic)
        backstory = config.get("backstory", "").replace("{topic}", self.topic)
        llm = config.get("llm", "gpt-4o-mini")

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
        )
    
    def _scraper_agent(self) -> Agent:
        config = self._agents_config.get("scraper", {})
        role = config.get("role", "").replace("{topic}", self.topic)
        goal = config.get("goal", "").replace("{topic}", self.topic)
        backstory = config.get("backstory", "").replace("{topic}", self.topic)
        llm = config.get("llm", "gpt-4o-mini")

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
        )

    def _run_research_plan_task(self, feedback: Optional[str] = None) -> str:
        """Execute research_plan_task and return result."""
        task_config = self._tasks_config.get("research_plan_task", {})

        description = task_config.get("description", "").replace("{topic}", self.topic)
        description = description.replace("{current_year}", self.current_year)

        if feedback:
            description = f"{description}\n\nIMPORTANT FEEDBACK FROM PREVIOUS REVIEW:\n{feedback}\n\nPlease revise the research plan to address the concerns above."

        expected_output = task_config.get("expected_output", "")

        agent = self._create_researcher_agent()

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_pydantic=ResearchPlan,
        )

        result = task.execute_sync()

        if result.pydantic:
            self.current_plan = ResearchPlan.model_validate(result.pydantic)
        return result.raw if result.raw else str(result.pydantic)

    def _run_plan_review_task(self, plan: ResearchPlan) -> PlanReview:
        """Execute plan_review_task and return result."""
        task_config = self._tasks_config.get("plan_review_task", {})

        rubric_context = self._get_rubric_context()
        description = task_config.get("description", "").replace("{topic}", self.topic)
        description = f"{description}\n\nResearch Plan to Review:\n{plan.model_dump_json(indent=2)}{rubric_context}"

        expected_output = task_config.get("expected_output", "")

        agent = self._create_plan_reviewer_agent()

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_pydantic=PlanReview,
        )

        result = task.execute_sync()

        if result.pydantic:
            review = PlanReview.model_validate(result.pydantic)
            self.current_review = review
            return review

        raise ValueError("Plan review did not return pydantic output")

    def _run_research_task(self) -> str:
        """Execute research_task and return result."""
        task_config = self._tasks_config.get("research_task", {})

        description = task_config.get("description", "").replace("{topic}", self.topic)
        description = description.replace("{current_year}", self.current_year)

        expected_output = task_config.get("expected_output", "")

        agent = self._create_researcher_agent()

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )

        result = task.execute_sync()
        return result.raw if result.raw else str(result.pydantic)

    def _run_source_review_task(self) -> str:
        """Execute source_review_task and return result."""
        task_config = self._tasks_config.get("source_review_task", {})

        rubric_context = self._get_rubric_context()
        description = task_config.get("description", "").replace("{topic}", self.topic)
        description = f"{description}{rubric_context}"

        expected_output = task_config.get("expected_output", "")

        agent = self._create_source_reviewer_agent()

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )

        result = task.execute_sync()
        return result.raw if result.raw else str(result.pydantic)

    def _run_reporting_task(self) -> str:
        """Execute reporting_task and return result."""
        task_config = self._tasks_config.get("reporting_task", {})

        description = task_config.get("description", "").replace("{topic}", self.topic)

        expected_output = task_config.get("expected_output", "")

        agent = self._create_reporting_agent()

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_file="report.md",
        )

        result = task.execute_sync()
        return result.raw if result.raw else str(result.pydantic)
    
    def _scraper_task(self, urls: list[str]) -> list[ScrapedDocument]:
        task_config = self._tasks_config.get("scraper_task", {})

        description = task_config.get("description", "").replace("{topic}", self.topic)

        agent = self._scraper_agent()
        expected_output = task_config.get("expected_output", "")

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_pydantic=list[ScrapedDocument],
        )

        result = task.execute_sync()

        if result.pydantic:
            self.scapered_docs = result.pydantic

        return result.raw if result.raw else str(result.pydantic)

    def _ask_human_decision(self) -> bool:
        """Ask human for decision after max revisions."""
        if not self.current_plan or not self.current_review:
            self.workflow_aborted = True
            return False

        plan_json = json.dumps(
            {
                "topic": self.current_plan.topic,
                "objectives": self.current_plan.objectives,
                "subtopics": self.current_plan.subtopics,
                "search_queries": self.current_plan.search_queries,
                "source_expectations": self.current_plan.source_expectations,
            },
            indent=2,
        )

        review_json = json.dumps(
            {
                "decision": self.current_review.decision,
                "rationale": self.current_review.rationale,
                "concerns": self.current_review.concerns,
                "revision_attempts": self.revision_attempts,
            },
            indent=2,
        )

        feedback_msg = f"""The research plan was not approved after maximum revision attempts.

=== RESEARCH PLAN ===
{plan_json}

=== PLAN REVIEW ===
{review_json}

Do you want to proceed with this plan anyway?
- [Yes - proceed to research and reporting]  
- [No - abort the workflow]"""

        print("\n" + "=" * 60)
        print("HUMAN DECISION REQUIRED")
        print("=" * 60)
        print(feedback_msg)
        print("=" * 60)

        user_input = input("\nDo you want to proceed? (yes/no): ").strip().lower()

        if user_input in ["yes", "y"]:
            self.human_approved = True
            self.current_review.decision = "approved"
            return True
        else:
            self.workflow_aborted = True
            return False

    def run(self, topic: str, current_year: str = "2026") -> str:
        """Execute the workflow."""
        self.topic = topic
        self.current_year = current_year
        self.revision_attempts = 0
        self.workflow_aborted = False
        self.human_approved = False

        print(f"\n{'=' * 60}")
        print(f"Starting KBB Workflow: {topic}")
        print(f"{'=' * 60}\n")

        self._execute_planning_phase()

        if self.workflow_aborted:
            return "Workflow aborted by user."

        self._execute_research_phase()

        if not self.workflow_aborted:
            self._execute_reporting_phase()

        return "Workflow completed successfully."

    def _execute_planning_phase(self):
        """Execute planning phase with revision loop."""
        while True:
            feedback = None
            if self.revision_attempts > 0 and self.current_review:
                concerns = self.current_review.concerns
                feedback = (
                    "Please address the following concerns from previous review:\n"
                )
                for concern in concerns:
                    feedback += f"- {concern}\n"

            print(
                f"\n[Plan Review Loop] Attempt {self.revision_attempts + 1}/{self.max_revisions}"
            )

            self._run_research_plan_task(feedback=feedback)

            if not self.current_plan:
                raise ValueError("Failed to create research plan")

            review = self._run_plan_review_task(self.current_plan)

            if review.decision == "approved":
                print("[Plan Review] Approved!")
                return

            if self.revision_attempts >= self.max_revisions:
                print(
                    f"[Plan Review] Max revisions reached ({self.max_revisions}). Asking human..."
                )
                self._ask_human_decision()
                return

            self.revision_attempts += 1
            print(
                f"[Plan Review] Revision requested. Attempt {self.revision_attempts}/{self.max_revisions}"
            )

    def _execute_research_phase(self):
        """Execute research and source review phase."""
        if self.human_approved:
            print("\n[Research] Human approved. Proceeding to research...")
        else:
            print("\n[Research] Proceeding to research...")

        self._run_research_task()
        print("[Research] Research completed.")

        print("[Source Review] Reviewing sources...")
        self._run_source_review_task()
        print("[Source Review] Source review completed.")

    def _execute_reporting_phase(self):
        """Execute reporting phase."""
        print("\n[Reporting] Generating final report...")
        self._run_reporting_task()
        print("[Reporting] Report generated.")


def run_workflow(topic: str, rubric_path: str = "", current_year: str = "2026") -> str:
    """Run the Kbb workflow."""
    workflow = KbbWorkflow(rubric_path=rubric_path)
    return workflow.run(topic=topic, current_year=current_year)


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "test topic"
    rubric = sys.argv[2] if len(sys.argv) > 2 else ""
    print(run_workflow(topic, rubric))
