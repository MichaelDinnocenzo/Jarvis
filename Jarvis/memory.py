import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from database import Database
from utils import get_timestamp, truncate

logger = logging.getLogger(__name__)

class MemoryManager:
    """Persistent memory system."""
    
    def __init__(self, db_path: str = "jarvis_memory.json", use_sqlite: bool = True):
        self.json_path = Path(db_path)
        self.use_sqlite = use_sqlite
        self.memory = self._load_memory()
        if use_sqlite:
            self.db = Database()
        self.stats = {"added": 0, "retrieved": 0}
        
    def _load_memory(self) -> List[Dict]:
        """Load memory from disk."""
        if self.json_path.exists():
            try:
                with open(self.json_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
        return []
        
    def _save_memory(self):
        """Save memory to disk."""
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def add(self, event_type: str, content: Any, metadata: Optional[Dict] = None):
        """Add memory event."""
        event = {
            "type": event_type,
            "content": truncate(str(content), 1000),
            "timestamp": get_timestamp(),
            "metadata": metadata or {}
        }
        self.memory.append(event)
        self.stats["added"] += 1
        
        if self.use_sqlite:
            self.db.insert_memory(event_type, str(content), metadata)
        
        self._save_memory()
        logger.info(f"Memory: +{event_type}")
    
    def get_recent(self, count: int = 10) -> List[str]:
        """Get recent memory events."""
        self.stats["retrieved"] += 1
        return [m["content"] for m in self.memory[-count:]]
    
    def get_by_type(self, event_type: str) -> List[Dict]:
        """Get memory by type."""
        self.stats["retrieved"] += 1
        return [m for m in self.memory if m["type"] == event_type]
    
    def search(self, query: str) -> List[Dict]:
        """Search memory by content."""
        results = []
        for m in self.memory:
            if query.lower() in m["content"].lower():
                results.append(m)
        return results
    
    def get_since(self, timestamp: str) -> List[Dict]:
        """Get memory since timestamp."""
        return [m for m in self.memory if m["timestamp"] > timestamp]
    
    def clear(self):
        """Clear memory."""
        self.memory = []
        self._save_memory()
        logger.info("Memory cleared")
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        event_types = {}
        for m in self.memory:
            event_types[m["type"]] = event_types.get(m["type"], 0) + 1
        
        return {
            "total_events": len(self.memory),
            "events_by_type": event_types,
            "stats": self.stats
        }
