from dataclasses import dataclass

@dataclass
class GiteaConfiguration(object):
    token: str
    base_url: str
    allowed_emails: str