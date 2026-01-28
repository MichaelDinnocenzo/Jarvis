import logging
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from agent import decide_action, initialize_jarvis
from memory import MemoryManager
from goals import GoalManager
from coder import Coder
from executor import Executor
from reflection import Reflector
from researcher import Researcher
from permissions import PermissionManager

# Optional imports with fallbacks
try:
    from embeddings import EmbeddingManager
except ImportError:
    EmbeddingManager = None

try:
    from voice import VoiceInterface
except ImportError:
    VoiceInterface = None

from cache import get_cache_manager
from metrics import get_metrics
from event_system import get_event_bus, EventType, Event
from config import load_config
from logger_config import setup_logging
from constants import *

setup_logging()
logger = logging.getLogger(__name__)

class Jarvis:
    """Autonomous AI software engineer."""
    
    def __init__(self):
        logger.info("Initializing Jarvis...")
        try:
            self.config = load_config()
            self.memory = MemoryManager(self.config.get("memory_db", "jarvis_memory.json"))
            self.goals = GoalManager(self.config.get("goals_db", "jarvis_goals.json"))
            self.coder = Coder()
            self.executor = Executor()
            self.reflector = Reflector(self.memory)
            self.researcher = Researcher()
            self.permissions = PermissionManager()
            
            # Optional modules
            self.embeddings = EmbeddingManager() if EmbeddingManager else None
            self.voice = VoiceInterface() if VoiceInterface else None
            
            self.cache = get_cache_manager()
            self.metrics = get_metrics()
            self.event_bus = get_event_bus()
            self.iteration_count = 0
            
            logger.info("Jarvis initialized successfully")
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            raise
    
    def run(self, iterations: int = 3, auto_mode: bool = False):
        """Main autonomous loop."""
        logger.info(f"Starting Jarvis - Iterations: {iterations}, Auto: {auto_mode}")
        self.event_bus.publish(Event(EventType.ITERATION_STARTED))
        
        for i in range(iterations):
            try:
                self.iteration_count = i + 1
                logger.info(f"\n{'='*80}")
                logger.info(f"--- Iteration {self.iteration_count}/{iterations} ---")
                logger.info(f"{'='*80}")
                
                self._execute_iteration(auto_mode)
                
            except Exception as e:
                logger.error(f"Iteration {self.iteration_count} failed: {e}", exc_info=True)
                self.memory.add("error", f"Iteration failed: {e}")
                self.event_bus.publish(Event(EventType.ERROR_OCCURRED, {"error": str(e)}))
        
        logger.info(f"\nJarvis cycle complete. Total iterations: {self.iteration_count}")
        self._generate_report()
        self.event_bus.publish(Event(EventType.ITERATION_COMPLETED))
    
    def _execute_iteration(self, auto_mode: bool):
        """Execute single iteration."""
        try:
            context = self._build_context()
            decision = decide_action(
                context,
                self.memory.get_recent(10),
                self.goals.get_active(),
                {"auto_mode": auto_mode, "iteration": self.iteration_count}
            )
            
            self.memory.add("decision", decision.get("analysis"))
            action_type = decision.get("action_type")
            
            logger.info(f"Action Type: {action_type}")
            
            # Route to handlers
            if action_type == "code_generation":
                self._handle_code_generation(decision)
            elif action_type == "code_refactor":
                self._handle_code_refactor(decision)
            elif action_type == "research":
                self._handle_research(decision)
            elif action_type == "reflection":
                self._handle_reflection(decision)
            elif action_type == "goal_update":
                self._handle_goal_update(decision)
            
            # Update goals
            for new_goal in decision.get("goals_update", []):
                self.goals.add(new_goal)
                
        except Exception as e:
            logger.error(f"Iteration execution failed: {e}", exc_info=True)
            raise
    
    def _handle_code_generation(self, decision: Dict):
        """Generate new code."""
        logger.info("Handling code generation...")
        for action in decision.get("actions", []):
            try:
                code = self.coder.generate(action)
                if self.permissions.check_code_safety(code):
                    result = self.executor.execute(code, dry_run=True)
                    self.memory.add("code_generated", action)
                    logger.info(f"Generated: {action[:50]}...")
            except Exception as e:
                logger.error(f"Code generation failed: {e}")
    
    def _handle_code_refactor(self, decision: Dict):
        """Refactor existing code."""
        logger.info("Handling code refactor...")
        for action in decision.get("actions", []):
            try:
                refactored = self.coder.refactor(action)
                self.memory.add("code_refactored", action)
            except Exception as e:
                logger.error(f"Refactoring failed: {e}")
    
    def _handle_research(self, decision: Dict):
        """Conduct research."""
        logger.info("Handling research...")
        for action in decision.get("actions", []):
            try:
                findings = self.researcher.search(action)
                self.memory.add("research", findings)
            except Exception as e:
                logger.error(f"Research failed: {e}")
    
    def _handle_reflection(self, decision: Dict):
        """Self-reflection."""
        logger.info("Handling reflection...")
        try:
            insights = self.reflector.analyze()
            self.memory.add("reflection", insights)
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
    
    def _handle_goal_update(self, decision: Dict):
        """Update goals."""
        logger.info("Handling goal update...")
        for goal in decision.get("goals_update", []):
            try:
                self.goals.add(goal)
            except Exception as e:
                logger.error(f"Goal update failed: {e}")
    
    def _build_context(self) -> str:
        """Build context for agent."""
        return f"""
Iteration: {self.iteration_count}
Active Goals: {len(self.goals.get_active())}
Timestamp: {datetime.now().isoformat()}
"""
    
    def _generate_report(self):
        """Generate final report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_iterations": self.iteration_count,
            "goals": self.goals.get_stats(),
            "memory": self.memory.get_stats(),
            "coder": self.coder.get_stats(),
            "executor": self.executor.get_stats(),
        }
        
        logger.info(f"\nFinal Report:\n{json.dumps(report, indent=2)}")
        
        try:
            with open("jarvis_report.json", 'w') as f:
                json.dump(report, f, indent=2)
            logger.info("Report saved to jarvis_report.json")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run(iterations=3, auto_mode=False)
    except KeyboardInterrupt:
        logger.info("Jarvis interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
