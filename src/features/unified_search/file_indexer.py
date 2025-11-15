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

    def _init_database(self):
        """Initialize the search index database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                name TEXT,
                extension TEXT,
                size INTEGER,
                last_modified REAL,
                inedexed_at real
            )
        ''')
        conn.exectue('CREATE INDEX IF NOT EXISTS idx_name ON files(name)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)')
        conn.commit()
        conn.close()