from abc import ABC, abstractmethod

from contracts.pr_url import PrUrl


class GitService(ABC):
    """
    Abstract base class defining the interface for Git service implementations.
    
    This class defines the contract for Git service implementations,
    requiring them to provide functionality for PR diffs, comments, and user access control.
    """
    @abstractmethod
    def get_pr_diff(self, pr_url : PrUrl) -> str:
        """
        Get the diff for a pull request.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            
        Returns:
            str: The diff content as a string
        """

    @abstractmethod
    def post_comment(self, pr_url : PrUrl, text : str) -> None:
        """
        Post a comment to a pull request.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            text (str): The comment text to post
        """

    @abstractmethod
    def is_allowed_user(self, login: str) -> bool:
        """
        Check if a user is allowed to perform actions.
        
        Args:
            login (str): The user's login/username
            
        Returns:
            bool: True if the user is allowed, False otherwise
        """
