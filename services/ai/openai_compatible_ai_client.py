import requests
from dataclasses import dataclass
from openai import OpenAI

from services.ai.ai_client import AIClient
from configuration.llm_configuration import LLMConfiguration



class OpenAICompatibleAIClient(AIClient):
    """
    A client for interacting with OpenAI-compatible API endpoints.
    
    This class implements the AIClient interface and provides functionality
    to communicate with OpenAI or compatible API servers for chat completions.
    
    Attributes:
        configuration (LLMConfiguration): Configuration for the LLM client
        client (OpenAI): The OpenAI client instance
    """
    def __init__(self, configuration: LLMConfiguration):
        """
        Initialize the OpenAICompatibleAIClient with the given configuration.
        
        Args:
            configuration (LLMConfiguration): Configuration containing API token and base URL
        """
        self.configuration = configuration
        self.client = OpenAI(
            api_key=configuration.token,
            base_url=configuration.base_url
        )

    def completions(self, messages: list[dict], model : str) -> str:
        """
        Get chat completions from the OpenAI-compatible API.
        
        Args:
            messages (list[dict]): List of message dictionaries containing role and content
            model (str): The model to use for completion
            
        Returns:
            str: The generated completion text, or None if no valid response
        """
        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=50000
        )
        if len(response.choices) == 0:
            return None
        return response.choices[0].message.content
