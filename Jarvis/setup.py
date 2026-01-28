"""Setup script for Jarvis."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_environment():
    """Setup environment and validate configuration."""
    
    print("="*80)
    print("Jarvis Setup")
    print("="*80)
    
    # Load .env
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found!")
        print("\nOption 1: Create .env file")
        print("  Add this line to .env:")
        print("  OPENAI_API_KEY=sk-proj-your-key-here")
        
        print("\nOption 2: Set environment variable (Windows)")
        print("  setx OPENAI_API_KEY 'sk-proj-your-key-here'")
        
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    # Check directories
    dirs_to_create = [
        Path("logs"),
        Path("data"),
        Path("cache")
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Directory ready: {dir_path}")
    
    print("\n✅ Setup complete! Ready to run Jarvis.")
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
