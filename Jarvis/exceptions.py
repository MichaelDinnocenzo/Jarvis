"""Custom exceptions for Jarvis."""

class JarvisException(Exception):
    """Base exception for all Jarvis errors."""
    pass

class CodeGenerationError(JarvisException):
    """Raised when code generation fails."""
    pass

class CodeExecutionError(JarvisException):
    """Raised when code execution fails."""
    pass

class MemoryError(JarvisException):
    """Raised when memory operations fail."""
    pass

class GoalError(JarvisException):
    """Raised when goal operations fail."""
    pass

class PermissionError(JarvisException):
    """Raised when permission check fails."""
    pass

class APIError(JarvisException):
    """Raised when API call fails."""
    pass

class ConfigError(JarvisException):
    """Raised when configuration is invalid."""
    pass

class ResearchError(JarvisException):
    """Raised when research fails."""
    pass

class ReflectionError(JarvisException):
    """Raised when reflection fails."""
    pass

class VoiceError(JarvisException):
    """Raised when voice operations fail."""
    pass
