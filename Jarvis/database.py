"""Database management for Jarvis."""

import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from constants import DB_PATH_MEMORY, DB_PATH_GOALS

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    priority INTEGER,
                    status TEXT,
                    created TEXT,
                    completed TEXT
                )
            """)
            
            # Cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp TEXT
                )
            """)
            
            conn.commit()
            logger.info("Database initialized")
    
    def insert_memory(self, event_type: str, content: str, metadata: Optional[Dict] = None):
        """Insert memory event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memory (event_type, content, timestamp, metadata) VALUES (?, ?, ?, ?)",
                (event_type, content, datetime.now().isoformat(), json.dumps(metadata or {}))
            )
            conn.commit()
    
    def get_memory(self, limit: int = 100) -> List[Dict]:
        """Get recent memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memory ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "event_type": r[1],
                    "content": r[2],
                    "timestamp": r[3],
                    "metadata": json.loads(r[4])
                }
                for r in rows
            ]
    
    def insert_cache(self, key: str, value: str):
        """Insert cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
            conn.commit()
    
    def get_cache(self, key: str) -> Optional[str]:
        """Get cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def clear_cache(self, older_than_days: int = 7):
        """Clear old cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM cache WHERE datetime(timestamp) < datetime('now', ? || ' days')",
                (f"-{older_than_days}",)
            )
            conn.commit()
