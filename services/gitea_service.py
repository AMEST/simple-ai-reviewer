import json
import logging
import re
from dataclasses import asdict

import requests

from configuration.gitea_configuration import GiteaConfiguration
from contracts.per_file_review_result import PerFileReviewResult
from contracts.pr_url import PrUrl

from services.git_service import GitService

class GiteaService(GitService):
    """
    Service for interacting with Gitea repositories.
    
    This class implements the GitService interface specifically for Gitea,
    providing functionality to work with pull requests and comments.
    
    Attributes:
        configuration (GiteaConfiguration): Configuration for Gitea API access
        logger (logging.Logger): Logger instance for service operations
    """
    def __init__(self, configuration : GiteaConfiguration):
        self.configuration = configuration
        self.logger = logging.getLogger(GiteaService.__name__)

    def get_pr_diff(self, pr_url : PrUrl) -> str:
        """
        Get the diff for a pull request from Gitea.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            
        Returns:
            str: The diff content as a string, or None if the request fails
        """
        diff_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/pulls/{pr_url.pr_number}.diff"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Accept": "application/json",
        }
        response = requests.get(diff_url, headers=headers, timeout=60 * 2) # get diff request with 2 minutes timeout
        if response.status_code == 200:
            return response.text
        self.logger.error("Error getting diff for %s. Status=%s.\n%s", diff_url, response.status_code, response.text)
        return None

    def post_comment(self, pr_url : PrUrl, text : str) -> None:
        """
        Post a comment to a Gitea pull request.
        
        Args:
            pr_url (PrUrl): The pull request URL object containing repository and PR information
            text (str): The comment text to post
        """
        comment_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/issues/{pr_url.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
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
        Check if a user is allowed to start a review based on configured allowed emails.
        !IMPORTANT! In Gitea used emails for user. In `login` param stored user email
        Args:
            login (str): For gites - is user email
            
        Returns:
            bool: True if the user is allowed, False otherwise
        """
        # If allowed emails not configured, empty or asterisk - all users allowed to start review
        if self.configuration.allowed_emails is None or self.configuration.allowed_emails == "" or self.configuration.allowed_emails == "*":
            return True
        if login is None or login == "":
            return False
        parsed_allowed_emails = re.split(r'[;,]\s*', self.configuration.allowed_emails.lower())
        return login.lower() in parsed_allowed_emails

    def create_review(self, pr_url : PrUrl, review_result : list[PerFileReviewResult]) -> str:
        create_review_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/pulls/{pr_url.pr_number}/reviews"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "event": "COMMENT",
            "body": "🤖 AI Code Per File Reviewed!",
            "comments": [asdict(r) for r in review_result]
        }
        for comment in payload["comments"]:
            comment["new_position"] = comment["line"]
            del comment["line"]
        response = requests.post(create_review_url, json=payload, headers=headers, timeout=60 * 2) # send comment with 2 minutes timeout
        if response.status_code != 200:
            self.logger.error("Error creating review for %s. Status=%s.\n%s\n%s", create_review_url, response.status_code, response.text, json.dumps(payload))
            return None
        response_json : dict = response.json()
        return response_json.get("id")

    def complete_review(self, pr_url : PrUrl, review_identifier : str) -> None:
        complete_review_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/pulls/{pr_url.pr_number}/reviews/{review_identifier}"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "event": "COMMENT",
            "body": "🤖 AI Code Review Per File completed!"
        }
        response = requests.post(complete_review_url, json=payload, headers=headers, timeout=60 * 2) # send comment with 2 minutes timeout
        if response.status_code in (200,201):
            return
        self.logger.error("Error completing review for %s. Status=%s.\n%s", complete_review_url, response.status_code, response.text)

