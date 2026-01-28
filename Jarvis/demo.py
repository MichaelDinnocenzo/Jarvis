"""Demo: Watch Jarvis code itself."""

import sys
from logger_config import setup_logging
from setup import setup_environment

setup_logging()

if not setup_environment():
    sys.exit(1)

from jarvis import Jarvis
import json

def main():
    print("\n" + "="*80)
    print("JARVIS AUTONOMOUS CODING DEMO")
    print("="*80)
    print("\nJarvis will autonomously:")
    print("  1. Analyze its own code")
    print("  2. Identify improvements")
    print("  3. Generate new code")
    print("  4. Refactor existing code")
    print("  5. Reflect on changes")
    print("\n" + "="*80 + "\n")
    
    try:
        jarvis = Jarvis()
        
        # Run 5 iterations of self-improvement
        jarvis.run(iterations=5, auto_mode=False)
        
        # Show what it learned
        print("\n" + "="*80)
        print("SELF-CODING RESULTS")
        print("="*80)
        
        # Get memory of self-improvements
        reflections = jarvis.memory.get_by_type("reflection")
        print(f"\n📝 Reflections ({len(reflections)}):")
        for r in reflections[-3:]:
            print(f"  - {r['content'][:100]}...")
        
        # Get generated code
        code_gen = jarvis.memory.get_by_type("code_generated")
        print(f"\n💻 Code Generated ({len(code_gen)}):")
        for c in code_gen[-3:]:
            print(f"  - {c['content'][:100]}...")
        
        # Get refactored code
        code_ref = jarvis.memory.get_by_type("code_refactored")
        print(f"\n🔧 Code Refactored ({len(code_ref)}):")
        for c in code_ref[-3:]:
            print(f"  - {c['content'][:100]}...")
        
        # Get goals completed
        goals_stats = jarvis.goals.get_stats()
        print(f"\n🎯 Goals:")
        print(f"  - Created: {goals_stats['created']}")
        print(f"  - Completed: {goals_stats['completed']}")
        print(f"  - Active: {goals_stats['active']}")
        
        print("\n" + "="*80)
        print("✅ Jarvis Self-Coding Complete!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
