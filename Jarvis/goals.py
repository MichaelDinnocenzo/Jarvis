import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from utils import get_timestamp
from constants import *

logger = logging.getLogger(__name__)

class GoalManager:
    """Manage Jarvis goals."""
    
    def __init__(self, db_path: str = "jarvis_goals.json"):
        self.db_path = Path(db_path)
        self.goals = self._load_goals()
        self.stats = {"created": 0, "completed": 0, "failed": 0}
        
    def _load_goals(self) -> List[Dict]:
        """Load goals from disk."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load goals: {e}")
        return []
        
    def _save_goals(self):
        """Save goals to disk."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.goals, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save goals: {e}")
    
    def add(self, goal: str, priority: int = GOAL_PRIORITY_MEDIUM) -> str:
        """Add new goal."""
        goal_id = f"goal_{len(self.goals)}_{datetime.now().timestamp()}"
        self.goals.append({
            "id": goal_id,
            "text": goal,
            "priority": priority,
            "status": STATUS_ACTIVE,
            "created": get_timestamp(),
            "completed": None,
            "attempts": 0
        })
        self.stats["created"] += 1
        self._save_goals()
        logger.info(f"Goal added: {goal[:50]}...")
        return goal_id
    
    def complete(self, goal_id: str):
        """Mark goal complete."""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = STATUS_COMPLETED
                goal["completed"] = get_timestamp()
                self.stats["completed"] += 1
                self._save_goals()
                logger.info(f"Goal completed: {goal['text'][:50]}...")
                break
    
    def fail(self, goal_id: str):
        """Mark goal failed."""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = STATUS_FAILED
                goal["attempts"] += 1
                self.stats["failed"] += 1
                self._save_goals()
                logger.warning(f"Goal failed: {goal['text'][:50]}...")
                break
    
    def block(self, goal_id: str):
        """Mark goal blocked."""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = STATUS_BLOCKED
                self._save_goals()
                logger.warning(f"Goal blocked: {goal['text'][:50]}...")
                break
    
    def get_active(self) -> List[str]:
        """Get active goals."""
        return [g["text"] for g in self.goals if g["status"] == STATUS_ACTIVE]
    
    def get_completed(self) -> List[str]:
        """Get completed goals."""
        return [g["text"] for g in self.goals if g["status"] == STATUS_COMPLETED]
    
    def get_by_priority(self, priority: int) -> List[Dict]:
        """Get goals by priority."""
        return [g for g in self.goals if g["priority"] == priority and g["status"] == STATUS_ACTIVE]
    
    def get_stats(self) -> Dict:
        """Get goal statistics."""
        return {
            "created": self.stats["created"],
            "completed": self.stats["completed"],
            "failed": self.stats["failed"],
            "active": len(self.get_active()),
            "total": len(self.goals)
        }
