import logging
import requests

from configuration.gitea_configuration import GiteaConfiguration

from contracts.gitea_pr_url import GiteaPrUrl

class GiteaService:
    def __init__(self, configuration : GiteaConfiguration):
        self.configuration = configuration
        self.logger = logging.getLogger(GiteaService.__name__)

    def get_pr_diff(self, pr_url : GiteaPrUrl) -> str:
        diff_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/pulls/{pr_url.pr_number}.diff"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Accept": "application/json",
        }
        response = requests.get(diff_url, headers=headers)
        if response.status_code == 200:
            return response.text
        self.logger.error(f"Error getting diff for {diff_url}. Status={response.status_code}.\n{response.text}")
        return None

    def post_comment(self, pr_url : GiteaPrUrl, text : str) -> None:
        comment_url = f"{self.configuration.base_url}/api/v1/repos/{pr_url.owner}/{pr_url.repo}/issues/{pr_url.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.configuration.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "body": text
        }
        requests.post(comment_url, json=payload, headers=headers)