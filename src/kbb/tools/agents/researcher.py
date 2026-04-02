
class ResearcherAgent(Agent):
    def __init__(self, llm, tools):
        self.tools = tools,
        self.llm = llm
