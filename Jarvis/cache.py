"""Caching system for Jarvis."""

import json
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from constants import CACHE_ENABLED

logger = logging.getLogger(__name__)

class CacheManager:
    """In-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if not CACHE_ENABLED:
            return None
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            return None
        
        entry["hits"] += 1
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value."""
        if not CACHE_ENABLED:
            return
        
        # Evict if over capacity
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl or self.ttl_seconds),
            "hits": 0
        }
        logger.debug(f"Cached: {key}")
    
    def delete(self, key: str):
        """Delete cache entry."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def _evict_oldest(self):
        """Evict oldest entry."""
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["created_at"])
        del self.cache[oldest_key]
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def stats(self) -> Dict:
        """Get cache statistics."""
        total_hits = sum(e["hits"] for e in self.cache.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "avg_hits": total_hits / len(self.cache) if self.cache else 0
        }

# Global cache instance
_cache = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get global cache manager."""
    return _cache
