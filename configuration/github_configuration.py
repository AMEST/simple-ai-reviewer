from dataclasses import dataclass

@dataclass
class GithubConfiguration(object):
    token: str
    allowed_logins: str