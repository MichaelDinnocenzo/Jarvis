import json
import logging
from pathlib import Path
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration."""
    config_file = Path(config_path)
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Config loaded from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30,
        "memory_db": "jarvis_memory.json",
        "goals_db": "jarvis_goals.json",
        "auto_save": True,
        "logging_level": "INFO",
        "max_iterations": 3,
        "safety_mode": True,
        "execute_code": False
    }

def save_config(config: Dict[str, Any], config_path: str = "config.json"):
    """Save configuration."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Config saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
