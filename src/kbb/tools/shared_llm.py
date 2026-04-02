import litellm
from crewai.llms.base_llm import BaseLLM

class SharedLLM(BaseLLM):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def call(self, messages, **kwargs):
        return self._call(messages, **kwargs)

    def _call(self, messages, **kwargs):
        agent_name = kwargs.get("agent_name")

        model = self.model_choice(agent_name)

        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                api_base=self.base_url
            )
        except Exception:
            response = litellm.completion(
                model="ollama/gpt-oss:20b",
                messages=messages,
                api_base=self.base_url
            )

        return response["choices"][0]["message"]["content"]

    def model_choice(self, agent_name):
        if agent_name == "researcher":
            return "local-gpt"
        elif agent_name == "reporting_analyst":
            return "gpt-4o-mini"
        return "gpt-4o-mini"