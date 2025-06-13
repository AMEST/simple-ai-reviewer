import requests
from dataclasses import dataclass

from services.ai.ai_client import AIClient
from configuration.llm_configuration import LLMConfiguration


@dataclass
class Response:
    """
    Represents the response from the Ollama API.
    
    Attributes:
        model (str): The model used for the response
        created_at (str): Timestamp of when the response was created
        message (dict): The response message content
        done (bool): Whether the response is complete
        done_reason (str): Reason for completion
        total_duration (int): Total duration of the request
        load_duration (int): Duration of model loading
        prompt_eval_count (int): Number of prompt evaluations
        prompt_eval_duration (int): Duration of prompt evaluation
        eval_count (int): Number of evaluations
        eval_duration (int): Duration of evaluations
    """
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
    """
    Configuration for the Ollama client.
    
    Attributes:
        base_url (str): Base URL for the Ollama API
        timeout (int): Request timeout in seconds
        health_timeout (int): Health check timeout in seconds
        default_model (str): Default model to use for requests
    """
    base_url: str
    timeout: int
    health_timeout: int
    default_model: str

class OllamaAIClient(AIClient):
    """
    A client for interacting with the Ollama API.
    
    This class implements the AIClient interface and provides functionality
    to communicate with Ollama API servers for chat completions.
    
    Attributes:
        configuration (LLMConfiguration): Configuration for the LLM client
    """
    def __init__(self, configuration: LLMConfiguration):
        """
        Initialize the OllamaAIClient with the given configuration.
        
        Args:
            configuration (LLMConfiguration): Configuration containing API base URL and other settings
        """
        self.configuration = configuration

    def completions(self, messages: list[dict], model : str) -> str:
        """
        Get chat completions from the Ollama API.
        
        Args:
            messages (list[dict]): List of message dictionaries containing role and content
            model (str): The model to use for completion
            
        Returns:
            str: The generated completion text, or None if the response is not complete
        """
        request_data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(f"{self.configuration.base_url}/api/chat", json=request_data, timeout=60 * 10)
        response.raise_for_status()
        response_object = Response(**response.json())
        if not response_object.done:
            return None
        return response_object.message.get("content")
