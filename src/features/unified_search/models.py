from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class SearchResult:
    path: str
    name: str
    score: float
    type: str = "file"
    extension: Optional[str] = None
    last_modified: Optional[float] = None
    size: Optional[int] = None
    