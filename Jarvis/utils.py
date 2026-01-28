"""Utility functions for Jarvis."""

import json
import hashlib
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def memoize(func: Callable) -> Callable:
    """Memoization decorator."""
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
        return wrapper
    return decorator

def measure_time(func: Callable) -> Callable:
    """Measure execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def truncate(text: str, length: int = 100) -> str:
    """Truncate text to length."""
    return text[:length] + "..." if len(text) > length else text

def format_json(obj: Any, indent: int = 2) -> str:
    """Format object as JSON."""
    try:
        return json.dumps(obj, indent=indent, default=str)
    except Exception as e:
        logger.error(f"JSON formatting failed: {e}")
        return str(obj)

def hash_text(text: str) -> str:
    """Generate hash of text."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def get_timestamp() -> str:
    """Get ISO format timestamp."""
    return datetime.now().isoformat()

def parse_json_safe(text: str) -> Optional[Dict]:
    """Safely parse JSON."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}")
        return None

def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def flatten_list(nested: List) -> List:
    """Flatten nested lists."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
