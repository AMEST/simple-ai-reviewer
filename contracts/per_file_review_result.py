from dataclasses import dataclass
from typing import Union

@dataclass
class PerFileReviewResult:
    body: str
    path: str
    line: Union[int, str]

    def __post_init__(self):
        if isinstance(self.line, str):
            if self.line.isnumeric():
                self.line = int(self.line)
            else:
                self.line = 0
