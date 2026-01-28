#!/usr/bin/env python
"""Quick launcher for Jarvis."""

import sys
import logging
from jarvis import Jarvis
from logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        auto_mode = sys.argv[2].lower() == "auto" if len(sys.argv) > 2 else False
        
        logger.info(f"Starting Jarvis with {iterations} iterations (auto_mode={auto_mode})")
        
        jarvis = Jarvis()
        jarvis.run(iterations=iterations, auto_mode=auto_mode)
        
        logger.info("Jarvis completed successfully")
        
    except Exception as e:
        logger.error(f"Jarvis failed: {e}", exc_info=True)
        sys.exit(1)
