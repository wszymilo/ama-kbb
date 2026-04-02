import litellm
from crewai.llms.base_llm import BaseLLM

class SharedLLM(BaseLLM):
    def __init__(self):
        super().__init__(model="local-gpt")

    def call(self, messages, **kwargs):
        return self._call(messages, **kwargs)

    def _call(self, messages, **kwargs):
        agent_name = kwargs.get("from_agent")

        model = self.model_choice(agent_name.role)

        print(f"Using model '{model}' for the LLM call.")

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
        if "Senior Data Researcher" in agent_name:
            return "local-gpt"
        elif "Reporting Analyst" in agent_name:
            return "local-gpt"
        return "gpt-4o-mini"