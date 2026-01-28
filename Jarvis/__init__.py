"""Jarvis - Autonomous AI Software Engineer"""

__version__ = "1.0.0"
__author__ = "Michael Dinn"
__all__ = [
    "Jarvis",
    "MemoryManager",
    "GoalManager",
    "Coder",
    "Executor",
    "Reflector",
    "Researcher",
    "PermissionManager",
    "VoiceInterface",
    "EmbeddingManager"
]

from jarvis import Jarvis
from memory import MemoryManager
from goals import GoalManager
from coder import Coder
from executor import Executor
from reflection import Reflector
from researcher import Researcher
from permissions import PermissionManager
from voice import VoiceInterface
from embeddings import EmbeddingManager
