from typing import Optional
from dataclasses import dataclass

@dataclass
class Pleat:
    name: str
    signal: Optional[bool] = None

    def __repr__(self):
        return f"Pleat({self.name}={self.signal})"

