from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from agents.researcher import ResearcherAgent
from kbb.tools.shared_llm import SharedLLM

@CrewBase
class Kbb:
    """Kbb crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    def __init__(self):
        self.shared_llm = SharedLLM()
    
    @agent
    def researcher(self) -> ResearcherAgent:
        return ResearcherAgent(
            llm=self.shared_llm,
            config=self.agents_config["researcher"]
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],  # type: ignore[index]
            verbose=True,
            llm=self.shared_llm,
        )
    
    @task
    def research_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_plan_task"],
            output_file="planner.md",
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],  # type: ignore[attr-defined,call-arg]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_task"],  # type: ignore[attr-defined,call-arg]
            output_file="report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Kbb crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            task_order=["research_plan_task", "research_task", "reporting_task"],
            verbose=True,
        )
