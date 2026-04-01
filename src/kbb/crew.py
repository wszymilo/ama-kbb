from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from kbb.config import get_config



@CrewBase
class Kbb:
    """Kbb crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def researcher(self) -> Agent:
        config = get_config()
        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[attr-defined]
            llm=config.MODEL,
            verbose=True,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        config = get_config()
        return Agent(
            config=self.agents_config["reporting_analyst"],  # type: ignore[attr-defined]
            llm=config.MODEL,
            verbose=True,
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
            verbose=True,
        )
