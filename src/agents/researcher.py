from time import sleep

from docutils.nodes import topic
from pydantic import ValidationError

from kbb.schemas.models import ResearchPlan, _utc_now
from crewai import Agent

class ResearcherAgent(Agent):
    def __init__(self, llm, config, verbose=True, **kwargs):
        super().__init__(config=config, verbose=verbose, **kwargs)
        self.llm = llm

    def generate_research_plan(self, topic: str) -> ResearchPlan:
        """
        Research a given topic and return a research plan.
        """

        system_prompt = """
        You are a helpful research assistant. 
        When given a research topic, you will generate a research plan that includes a list of search queries to explore the topic. 
        The research plan should be concise and focused on the main topic.
        Generate a research plan with the fields:
            - topic: str
            - search_queries: list[str]
            - created_at: str (ISO datetime)
        """

        for _ in range(3):
            try:
                plan: ResearchPlan = self.llm.call(
                    topic,
                    system_prompt=system_prompt,
                    response_model=ResearchPlan
                )
                return plan
            except ValidationError:
                sleep(0.5)

        print("Failed to generate a valid research plan, returning fallback.")
        
        return ResearchPlan(topic=topic, search_queries=[], created_at=_utc_now())
    
    def research(self, topic: str) -> str:
        system_prompt = """
        You are a helpful research assistant.
        """

        response = self.llm.call(topic, system_prompt=system_prompt)

        return response