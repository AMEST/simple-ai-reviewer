from dataclasses import dataclass
import re

@dataclass
class GiteaPrUrl:
    gitea_url : str
    owner : str
    repo : str
    pr_number: int

    @staticmethod
    def create_from_url(url : str):
        pattern = r"^(https?://[^/]+)/([^/]+)/([^/]+)/pulls/(\d+)/?$"
        match = re.match(pattern, url)
        if not match:
            alt_pattern = r"^(https?://[^/]+)/([^/]+)/([^/]+)/pulls/(\d+)$"
            match = re.match(alt_pattern, url)
            if not match:
                raise ValueError(f"Invalid Gitea pull request URL format: {url}")
        gitea_url = match.group(1)
        owner = match.group(2)
        repo = match.group(3)
        pr_number = match.group(4)
        return GiteaPrUrl(gitea_url, owner, repo, pr_number)