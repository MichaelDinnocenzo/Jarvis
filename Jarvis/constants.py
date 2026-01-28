"""Global constants for Jarvis."""

# Models
DEFAULT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Paths
DB_PATH_MEMORY = "jarvis_memory.json"
DB_PATH_GOALS = "jarvis_goals.json"
DB_PATH_CACHE = "jarvis_cache.json"
CONFIG_PATH = "config.json"
LOG_PATH = "jarvis.log"

# Timeouts
DEFAULT_TIMEOUT = 30
VOICE_TIMEOUT = 10
API_TIMEOUT = 60

# Limits
MAX_ITERATIONS = 10
MAX_MEMORY_SIZE = 10000
MAX_GOALS = 100
MAX_CODE_LENGTH = 5000
MAX_TOKENS = 2000

# Thresholds
MIN_CONFIDENCE = 0.5
MIN_QUALITY_SCORE = 60
MAX_REFLECTION_INTERVAL = 5

# Safety
SAFETY_MODE = True
BLOCK_DANGEROUS_CODE = True
REQUIRE_DRY_RUN = False

# Performance
CACHE_ENABLED = True
EMBEDDINGS_CACHE_SIZE = 1000
RESEARCH_CACHE_SIZE = 500

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Voice
VOICE_ENABLED = False
VOICE_RATE = 150
VOICE_VOLUME = 1.0

# Reflection
REFLECTION_ENABLED = True
REFLECTION_INTERVAL = 5
REFLECTION_DEPTH = 3

# Goals
GOAL_PRIORITY_CRITICAL = 1
GOAL_PRIORITY_HIGH = 3
GOAL_PRIORITY_MEDIUM = 5
GOAL_PRIORITY_LOW = 8

# Status codes
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_BLOCKED = "blocked"
STATUS_FAILED = "failed"

# Action types
ACTION_CODE_GENERATION = "code_generation"
ACTION_CODE_REFACTOR = "code_refactor"
ACTION_RESEARCH = "research"
ACTION_REFLECTION = "reflection"
ACTION_GOAL_UPDATE = "goal_update"
ACTION_ERROR = "error"
