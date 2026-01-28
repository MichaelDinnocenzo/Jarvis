"""Task scheduling for Jarvis."""

import logging
import threading
from typing import Callable, Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class Task:
    """Scheduled task."""
    
    def __init__(self, name: str, func: Callable, priority: TaskPriority = TaskPriority.NORMAL):
        self.name = name
        self.func = func
        self.priority = priority
        self.created_at = datetime.now()
        self.executed = False
        self.result = None
    
    def execute(self) -> Any:
        """Execute task."""
        try:
            self.result = self.func()
            self.executed = True
            logger.info(f"Task executed: {self.name}")
            return self.result
        except Exception as e:
            logger.error(f"Task failed: {self.name} - {e}")
            raise

class Scheduler:
    """Task scheduler."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.running = False
        self.thread = None
    
    def schedule(self, name: str, func: Callable, priority: TaskPriority = TaskPriority.NORMAL) -> Task:
        """Schedule a task."""
        task = Task(name, func, priority)
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority.value)
        logger.info(f"Task scheduled: {name}")
        return task
    
    def execute_all(self):
        """Execute all tasks."""
        for task in self.tasks:
            try:
                task.execute()
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
    
    def execute_priority(self, priority: TaskPriority):
        """Execute tasks of priority."""
        for task in self.tasks:
            if task.priority == priority:
                try:
                    task.execute()
                except Exception as e:
                    logger.error(f"Task execution failed: {e}")
    
    def start_async(self):
        """Start async execution."""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started")
    
    def _run_loop(self):
        """Main scheduler loop."""
        while self.running:
            self.execute_all()
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Scheduler stopped")
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        executed = sum(1 for t in self.tasks if t.executed)
        return {
            "total_tasks": len(self.tasks),
            "executed": executed,
            "pending": len(self.tasks) - executed
        }
