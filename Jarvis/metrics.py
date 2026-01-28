"""Metrics and monitoring for Jarvis."""

import logging
import time
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and track metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_metric(self, name: str, value: float):
        """Record metric value."""
        self.metrics[name].append(value)
        logger.debug(f"Metric recorded: {name}={value}")
    
    def increment_counter(self, name: str, amount: int = 1):
        """Increment counter."""
        self.counters[name] += amount
    
    def get_metric_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for metric."""
        values = self.metrics.get(name, [])
        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all metrics and counters."""
        return {
            "metrics": {name: self.get_metric_stats(name) for name in self.metrics},
            "counters": dict(self.counters),
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
    
    def reset(self):
        """Reset metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.start_time = datetime.now()
        logger.info("Metrics reset")

# Global metrics instance
_metrics = MetricsCollector()

def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    return _metrics
