import requests
from dataclasses import dataclass

from services.ai.ai_client import AIClient
from configuration.llm_configuration import LLMConfiguration


@dataclass
class Response:
    model: str
    created_at: str
    message: dict
    done: bool
    done_reason: str
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int

@dataclass
class OllamaClientConfiguration:
    base_url: str
    timeout: int
    health_timeout: int
    default_model: str

class OllamaAIClient(AIClient):
    def __init__(self, configuration: LLMConfiguration):
        self.configuration = configuration

    def completions(self, messages: list[dict], model : str) -> str:
        request_data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(f"{self.configuration.base_url}/api/chat", json=request_data)
        response.raise_for_status()
        response_object = Response(**response.json())
        if not response_object.done:
            return None
        return response_object.message.get("content")