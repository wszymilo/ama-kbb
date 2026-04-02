from kbb.schemas.models import ResearchPlan
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
        Always respond with JSON in the following format:
        {
          "topic": str,
          "search_queries": list[str],
          "created_at": str (ISO datetime)
        }
        """
        response = self.llm.call(topic, system_prompt=system_prompt)

        research_plan = ResearchPlan.model_validate_json(response.content)

        return research_plan
    
    def research(self, topic: str) -> str:
        system_prompt = """
        You are a helpful research assistant.
        """

        response = self.llm.call(topic, system_prompt=system_prompt)

        return response