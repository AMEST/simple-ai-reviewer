from dataclasses import dataclass

@dataclass
class ReviewTask:
    pull_request_url: str
    user_message: str = None