import requests
from dataclasses import dataclass
from openai import OpenAI

from services.ai.ai_client import AIClient
from configuration.llm_configuration import LLMConfiguration



class OpenAICompatibleAIClient(AIClient):
    def __init__(self, configuration: LLMConfiguration):
        self.configuration = configuration
        self.client = OpenAI(
            api_key=configuration.token,
            base_url=configuration.base_url
        )

    def completions(self, messages: list[dict], model : str) -> str:
        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=50000
        )
        if len(response.choices) == 0:
            return None
        return response.choices[0].message.content