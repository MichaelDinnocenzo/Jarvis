"""Event-driven system for Jarvis."""

import logging
from typing import Callable, Dict, List, Any
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types."""
    CODE_GENERATED = "code_generated"
    CODE_REFACTORED = "code_refactored"
    GOAL_COMPLETED = "goal_completed"
    GOAL_FAILED = "goal_failed"
    REFLECTION_DONE = "reflection_done"
    RESEARCH_DONE = "research_done"
    ERROR_OCCURRED = "error_occurred"
    ITERATION_STARTED = "iteration_started"
    ITERATION_COMPLETED = "iteration_completed"

class Event:
    """Event object."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()

class EventBus:
    """Event bus for publish/subscribe."""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event: Event):
        """Publish event."""
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Event callback failed: {e}")
        logger.debug(f"Event published: {event.type.value}")
    
    def clear(self):
        """Clear all subscribers."""
        self.subscribers.clear()

from datetime import datetime

# Global event bus
_event_bus = EventBus()

def get_event_bus() -> EventBus:
    """Get global event bus."""
    return _event_bus
