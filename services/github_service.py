import logging
import re

import requests

from configuration.github_configuration import GithubConfiguration
from contracts.pr_url import PrUrl

from services.git_service import GitService

class GithubService(GitService):
    """
    Service for interacting with GitHub repositories.
    
    This class implements the GitService interface specifically for GitHub,
    providing functionality to work with pull requests and comments.
    
    Attributes:
        configuration (GithubConfiguration): Configuration for GitHub API access
        logger (logging.Logger): Logger instance for service operations
    """
    def __init__(self, configuration : GithubConfiguration):
        self.configuration = configuration
        self.logger = logging.getLogger(GithubService.__name__)

    def get_pr_diff(self, pr_url : PrUrl) -> str:
        """
        Get the diff for a pull request from GitHub.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            
        Returns:
            str: The diff content as a string, or None if the request fails
        """
        diff_url = f"https://api.github.com/repos/{pr_url.owner}/{pr_url.repo}/pulls/{pr_url.pr_number}.diff"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Accept": "application/vnd.github.v3.diff",
        }
        response = requests.get(diff_url, headers=headers, timeout=60 * 2) # get diff request with 2 minutes timeout
        if response.status_code == 200:
            return response.text
        self.logger.error("Error getting diff for %s. Status=%s.\n%s", diff_url, response.status_code, response.text)
        return None

    def post_comment(self, pr_url : PrUrl, text : str) -> None:
        """
        Post a comment to a GitHub pull request.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            text (str): The comment text to post
        """
        comment_url = f"https://api.github.com/repos/{pr_url.owner}/{pr_url.repo}/issues/{pr_url.pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        payload = {
            "body": text
        }
        response = requests.post(comment_url, json=payload, headers=headers, timeout=60 * 2) # send comment with 2 minutes timeout
        if response.status_code in (200,201):
            return
        self.logger.error("Error post comment to %s/%s #%s. Status=%s.\n%s", pr_url.owner, pr_url.repo, pr_url.pr_number, response.status_code, response.text)

    def is_allowed_user(self, login: str) -> bool:
        """
        Check if a user is allowed to start a review based on configured allowed logins.
        
        Args:
            login (str): The user's login/username
            
        Returns:
            bool: True if the user is allowed, False otherwise
        """
        # If allowed emails not configured, empty or asterisk - all users allowed to start review
        if self.configuration.allowed_logins is None or self.configuration.allowed_logins == "" or self.configuration.allowed_logins == "*":
            return True
        if login is None or login == "":
            return False
        parsed_allowed_logins = re.split(r'[;,]\s*', self.configuration.allowed_logins.lower())
        return login.lower() in parsed_allowed_logins
