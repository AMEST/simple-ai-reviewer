import logging
import re

import requests

from configuration.gitea_configuration import GiteaConfiguration
from contracts.gitea_pr_url import GiteaPrUrl


class GiteaService:
    """ Service with implementation of interaction with Gitea """
    def __init__(self, configuration : GiteaConfiguration):
        self.configuration = configuration
        self.logger = logging.getLogger(GiteaService.__name__)

    def get_pr_diff(self, pr_url : GiteaPrUrl) -> str:
        """ Getting PR diff from Gitea"""
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

    def post_comment(self, pr_url : GiteaPrUrl, text : str) -> None:
        """ Post comment to PR """
        comment_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/issues/{pr_url.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "body": text
        }
        requests.post(comment_url, json=payload, headers=headers, timeout=60 * 2) # send comment with 2 minutes timeout

    def is_allowed_user(self, email: str) -> bool:
        """ Check user is allowed to start review """
        # If allowed emails not configured, empty or asterisk - all users allowed to start review
        if self.configuration.allowed_emails is None or self.configuration.allowed_emails == "" or self.configuration.allowed_emails == "*":
            return True
        if email is None or email == "":
            return False
        parsed_allowed_emails = re.split(r'[;,]\s*', self.configuration.allowed_emails.lower())
        return email.lower() in parsed_allowed_emails
