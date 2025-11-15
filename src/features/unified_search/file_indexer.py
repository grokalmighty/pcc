import sqlite3
import time
from pathlib import Path
from typing import List, sSet
from .models import IndexStats

class FileIndexer:
    def __init__(self, db_path: str = "data/search_index.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()