"""Launcher for Jarvis."""

import sys
import logging
from pathlib import Path

# Setup
from setup import setup_environment
if not setup_environment():
    print("\n⚠️  Setup failed. Exiting.")
    sys.exit(1)

# Load logger
from logger_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Import Jarvis
try:
    from jarvis import Jarvis
    logger.info("Jarvis imported successfully")
except Exception as e:
    logger.error(f"Failed to import Jarvis: {e}", exc_info=True)
    sys.exit(1)

def main():
    """Main entry point."""
    try:
        iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        auto_mode = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else False
        
        logger.info(f"Starting Jarvis with {iterations} iterations (auto_mode={auto_mode})")
        
        jarvis = Jarvis()
        jarvis.run(iterations=iterations, auto_mode=auto_mode)
        
        logger.info("✅ Jarvis completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("⚠️  Jarvis interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
