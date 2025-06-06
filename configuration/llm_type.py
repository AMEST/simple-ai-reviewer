from enum import Enum

class LLMType(Enum):
    Ollama = "ollama"
    OpenAICompatible = "openai-compatible"