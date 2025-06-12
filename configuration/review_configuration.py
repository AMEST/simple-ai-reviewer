from dataclasses import dataclass
from typing import Union
from configuration.language import Language

@dataclass
class ReviewConfiguration:
    language: Union[Language, str]
    ignore_files: Union[list[str], str]

    def __post_init__(self):
        if isinstance(self.language, str):
            try:
                self.language = Language(self.language)
            except ValueError:
                raise ValueError(f"Invalid Language: {self.language}. Valid types are: {[t.value for t in Language]}")
        if isinstance(self.ignore_files, str):
            self.ignore_files = [f.strip() for f in self.ignore_files.split(",") if f.strip()]
