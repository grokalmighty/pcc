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

    def index_directory(self, directory: str) -> int:
        """Index a directory and return number of files indexed"""
        dir_path = Path(directory).expanduser()
        if not dir_path.exists():
            return 0

        conn = sqlite3.connect(self.db_path)
        count = 0

        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    conn.execute('''
                        INSERT OR REPLACE INTO files
                        (path, name, extension, size, last_modified, indexed_at)
                        VALUES(?, ?, ?, ?, ?, ?)
                    ''', (
                        str(file_path),
                        file_path.name,
                        file_path.suffix.lower(),
                        stat.st_size,
                        stat.st_mtime,
                        time.time()
                    ))
                    count += 1
                except (OSError, PermissionError) as e:
                    # Skip files that can't be accessed
                    continue
            
        conn.commit()
        conn.close()
        return count
    
    def get_index_stats(self) -> IndexStats:
        """Get statistics about the index"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT COUNT(*), COALESCE(SUM(size), 0), MAX(indexed_at)
            FROM files
        ''')
        total_files, total_size, last_indexed = cursor.fetchone()

        cursor = conn.execute('SELECT DISTINCT path FROM files LIMIT 1000')
        sample_files = [row[0] for row in cursor.fetchall()]

        # Extract unique directories from sample files
        directories = set()
        for file_path in sample_files:
            directories.add(str(Path(file_path).parent))

        conn.close()

        return IndexStats(
            total_files=total_files,
            total_size=total_size,
            last_indexed=last_indexed or 0,
            directories=list(directories)
        )