from abc import ABC, abstractmethod

class AIClient(ABC):
    @abstractmethod
    def completions(self, messages: list[dict], model : str) -> str:
        """Send messages with history to LLM form chat completion"""