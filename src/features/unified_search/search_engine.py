import os 
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from rapidfuzz import process, fuzz

class SearchEngine:
    def __init__(self, config):
        self.config = config
        self.db_path = Path("data/search_index.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_databse()
        self._index_files()
    
    def _init_databse(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS file (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                name TEXT,
                extension TEXT,
                last_modified REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def _index_files(self):
        """Index files from configured directories"""
        conn = sqlite3.connect(self.db_path)

        for directory in self.config.get('search_directories'):
            dir_path = Path(directory).expanduser()
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    conn.execute('''
                        INSERT OR REEPLACE INTO files
                        (path, name, extension, last_modified)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        str(file_path),
                        file_path.name,
                        file_path.suffix.lower(),
                        file_path.stat().st_mtime
                    ))
        
        conn.commit()
        conn.close()
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search for files"""
        if not query:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT path, name FROM files')
        files = cursor.fetchall()
        conn.close()

        # Fuzzy match against filenames
        filenames = [file[1] for file in files]
        matches = process.extract(
            query, filenames,
            scorer=fuzz.partial_ratio,
            limit=limit
        )

        results = []
        for match in matches:
            filename, score, idx = match
            
            # Find the original file path
            file_path = next((f[0] for f in files if f[1] == filename), None)
            if file_path:
                results.append({
                    'path': file_path,
                    'name': filename,
                    'score': score,
                    'type': 'file'
                })
        
        return results
    
    def open_file(self, file_path: str) -> bool:
        """Open file with system default application"""
        try:
            if os.name == 'nt': # Windows
                os.startfile(file_path)
            elif os.name == 'posix': # max/Linux
                os.system(f'open " {file_path}"' if sys.platform == 'darwin'
                          else f'xdg-open "{file_path}"')
            return True
        except Exception as e:
            print(f"Failed to open file: {e}")
            return False