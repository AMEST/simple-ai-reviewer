from dataclasses import dataclass
from typing import Union
from configuration.language import Language

@dataclass
class ReviewConfiguration:
    language: Union[Language, str]

    def __post_init__(self):
        if isinstance(self.language, str):
            try:
                self.language = Language(self.language)
            except ValueError:
                raise ValueError(f"Invalid Language: {self.language}. Valid types are: {[t.value for t in Language]}")
