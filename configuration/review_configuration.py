from dataclasses import dataclass
from typing import Union
from configuration.language import Language

@dataclass
class ReviewConfiguration:
    language: Union[Language, str]
    ignore_files: Union[list[str], str]
    review_as_comments: Union[bool, str]
    review_as_conversations: Union[bool, str]


    def __post_init__(self):
        if isinstance(self.language, str):
            try:
                self.language = Language(self.language)
            except ValueError:
                raise ValueError(f"Invalid Language: {self.language}. Valid types are: {[t.value for t in Language]}")
        if isinstance(self.ignore_files, str):
            self.ignore_files = [f.strip() for f in self.ignore_files.split(",") if f.strip()]
        if isinstance(self.review_as_comments, str):
            self.review_as_comments = True if self.review_as_comments.lower() == "true" else False
        if isinstance(self.review_as_conversations, str):
            self.review_as_conversations = True if self.review_as_conversations.lower() == "true" else False
