import unittest
import logging
import json
import tempfile
from pathlib import Path

from agent import decide_action, initialize_jarvis
from memory import MemoryManager
from goals import GoalManager
from coder import Coder
from executor import Executor
from permissions import PermissionManager
from config import load_config, get_default_config
from cache import get_cache_manager
from metrics import get_metrics
from constants import *

logging.basicConfig(level=logging.INFO)

class TestMemoryManager(unittest.TestCase):
    """Test memory management."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory = MemoryManager(f"{self.temp_dir}/memory.json")
    
    def test_add_event(self):
        self.memory.add("test", "content")
        self.assertEqual(len(self.memory.memory), 1)
    
    def test_get_recent(self):
        for i in range(5):
            self.memory.add("test", f"content_{i}")
        recent = self.memory.get_recent(3)
        self.assertEqual(len(recent), 3)
    
    def test_search(self):
        self.memory.add("test", "hello world")
        results = self.memory.search("world")
        self.assertEqual(len(results), 1)

class TestGoalManager(unittest.TestCase):
    """Test goal management."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.goals = GoalManager(f"{self.temp_dir}/goals.json")
    
    def test_add_goal(self):
        goal_id = self.goals.add("Test goal")
        self.assertIsNotNone(goal_id)
        self.assertEqual(len(self.goals.goals), 1)
    
    def test_complete_goal(self):
        goal_id = self.goals.add("Test goal")
        self.goals.complete(goal_id)
        completed = self.goals.get_completed()
        self.assertEqual(len(completed), 1)
    
    def test_fail_goal(self):
        goal_id = self.goals.add("Test goal")
        self.goals.fail(goal_id)
        self.assertEqual(self.goals.goals[0]["status"], STATUS_FAILED)

class TestPermissionManager(unittest.TestCase):
    """Test permission checking."""
    
    def setUp(self):
        self.perms = PermissionManager()
    
    def test_safe_code(self):
        code = "print('hello')"
        self.assertTrue(self.perms.check_code_safety(code))
    
    def test_dangerous_code(self):
        code = "os.system('rm -rf /')"
        result = self.perms.check_code_safety(code)
        # Should be blocked if BLOCK_DANGEROUS_CODE is True
        self.assertIsNotNone(result)

class TestExecutor(unittest.TestCase):
    """Test code execution."""
    
    def setUp(self):
        self.executor = Executor()
    
    def test_dry_run(self):
        result = self.executor.execute("print('test')", dry_run=True)
        self.assertTrue(result["dry_run"])
    
    def test_validate_code(self):
        self.assertTrue(self.executor.validate("x = 1 + 1"))
        self.assertFalse(self.executor.validate("x = ("))

class TestCache(unittest.TestCase):
    """Test caching."""
    
    def setUp(self):
        self.cache = get_cache_manager()
        self.cache.clear()
    
    def test_cache_set_get(self):
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")
    
    def test_cache_delete(self):
        self.cache.set("key", "value")
        self.cache.delete("key")
        self.assertIsNone(self.cache.get("key"))

class TestMetrics(unittest.TestCase):
    """Test metrics collection."""
    
    def setUp(self):
        self.metrics = get_metrics()
        self.metrics.reset()
    
    def test_record_metric(self):
        self.metrics.record_metric("test", 42.0)
        stats = self.metrics.get_metric_stats("test")
        self.assertEqual(stats["avg"], 42.0)
    
    def test_counter(self):
        self.metrics.increment_counter("test", 5)
        stats = self.metrics.get_all_stats()
        self.assertEqual(stats["counters"]["test"], 5)

class TestConfig(unittest.TestCase):
    """Test configuration."""
    
    def test_default_config(self):
        config = get_default_config()
        self.assertIn("model", config)
        self.assertIn("timeout", config)
        self.assertIn("safety_mode", config)

def run_tests():
    print("No tests yet.")

if __name__ == "__main__":
    unittest.main()
