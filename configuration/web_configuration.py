from dataclasses import dataclass

@dataclass
class WebConfiguration(object):
    token: str
    host: str
    port: int