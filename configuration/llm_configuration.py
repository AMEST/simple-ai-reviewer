from dataclasses import dataclass
from typing import Union
from configuration.llm_type import LLMType

@dataclass
class LLMConfiguration:
    type: Union[LLMType, str]
    base_url: str
    model: str
    token: str

    def __post_init__(self):
        if isinstance(self.type, str):
            try:
                self.type = LLMType(self.type)
            except ValueError:
                raise ValueError(f"Invalid LLM type: {self.type}. Valid types are: {[t.value for t in LLMType]}")
