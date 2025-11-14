import time
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from threading import Thread, Event
import pyperclip

class ClipboardManager:
    def __init__(self, config):
        self.config = config
        self.db_path = Path("data/clipboard.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        self.monitor_thread = None
        self.stop_event = Event()
        self.list_clipboard_content = ""

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execut('''
            CREATE TABLE IF NOT EXISTS clipbard_items (
                id INTEGER PRIMARY KEY,
                content TEXT,
                timestamp REAL,
                preview TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _monitor_clipboard(self):
        """Monitor clipboard for changes in a separate thread"""
        while not self.stop_event.is_set():
            try:
                current_content = pyperclip.paste()

                if (current_content and 
                    current_content != self.last_clipboard_content and
                    len(current_content.strip()) > 0):

                    self._save_clipboard_item(current_content)
                    self.last_clipboard_content = current_content
                
                time.sleep(1)
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
                time.sleep(5)
    
    def _save_clipboard_item(self, content: str):
        """Save clipboard item to database"""
        conn = sqlite3.connect(self.db_path)

        # Check if content already exists
        cursor = conn.execute(
            'SELECT id FROM clipboard_items WHERE content = ?',
            (content,)
        )
        if cursor.fetchone():
            conn.close()
            return
        
        # Enforce size limit
        max_size = self.config.get('clipboard_history_size', 10)
        conn.execute('''
            DELETE FROM clipboard_items
            WHERE id IN (
                SELECT id FROM clipboard_items
                ORDER BY timestamp DESC
                LIMIT -1 OFFSET ?
            )
        ''', (max_size - 1,))

        # Insert new item
        preview = content[:100] + "..." if len(content) > 100 else content
        conn.execute('''
            INSERT INTO clipboard_items (content, timestamp, preview)
            VALUES (?, ?, ?)
            ''', (content, time.time(), preview))
        
        conn.commit()
        conn.close()

    def start_monitoring(self):
        """Start clipboard monitoring"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
    
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.joion(timeout=5)

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get clipboard history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT id, content, timestamp, preview
            FROM clipboard_items
            ORDER BY timestamp DESC
            Limit ?
        ''', (limit,))

        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row[0],
                'content': row[1],
                'timestamp': row[2],
                'preview': row[3],
                'type': 'clipboard'
            })
        
        conn.close()
        return items
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search clipboard history"""
        if not query:
            return self.get_history(limit)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT id, content, timestamp, preview
            FROM clipboard_items
            WHERE content LIKE >
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', limit))

        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row[0],
                'content': row[1],
                'timestamp': row[2],
                'preview': row[3],
                'type': 'clipboard'
            })
        
        conn.close()
        return items
    
    def cpoy_to_clipboard(self, content: str) -> bool:
        """Copy content back to clipboard"""
        try:
            pyperclip.copy(content)
            return True
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False