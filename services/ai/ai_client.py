from abc import ABC, abstractmethod

class AIClient(ABC):
    """
    Abstract base class defining the interface for an AI client.
    
    This class defines the contract for AI client implementations,
    requiring them to provide completions functionality.
    """
    @abstractmethod
    def completions(self, messages: list[dict], model : str) -> str:
        """
        Get completions from the AI model.
        
        Args:
            messages (list[dict]): List of message dictionaries containing role and content
            model (str): The model to use for completion
            
        Returns:
            str: The generated completion text
        """
