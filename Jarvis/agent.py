import os
import json
import logging
from typing import Dict, List, Any
from api_client import get_api_client
from utils import truncate, measure_time, retry
from metrics import get_metrics
from constants import DEFAULT_MODEL, MAX_TOKENS, MIN_CONFIDENCE

logger = logging.getLogger(__name__)
metrics = get_metrics()

SYSTEM = """
You are Jarvis, an autonomous AI software engineer capable of self-improvement.

Capabilities:
- Analyze and refactor code
- Suggest architectural improvements
- Create and manage coding goals
- Generate implementation plans
- Identify code quality issues
- Propose optimizations
- Learn from past decisions
- Reflect on performance

Decision Format - ALWAYS respond in valid JSON:
{
    "analysis": "Brief analysis of situation",
    "action_type": "code_generation|code_refactor|research|reflection|goal_update",
    "actions": ["action1", "action2"],
    "goals_update": ["new_goal1"],
    "confidence": 0.0-1.0,
    "reasoning": "Why this action?"
}
"""

@retry(max_attempts=3, delay=1.0)
@measure_time
def decide_action(context: str, memory: List[str], goals: List[str], metadata: Dict = None) -> Dict[str, Any]:
    """Query Jarvis to decide next action."""
    api_client = get_api_client()
    
    try:
        memory_context = "\n".join(memory[-10:]) if memory else "No prior context"
        goals_context = "\n".join(f"- {g}" for g in goals[:5]) if goals else "No goals"
        meta_str = json.dumps(metadata or {}, indent=2)[:500]
        
        enhanced_context = f"""
Context: {context}

Recent Memory (last 10):
{truncate(memory_context, 500)}

Current Goals (top 5):
{truncate(goals_context, 300)}

Metadata:
{meta_str}
"""
        
        response = api_client.create_completion(
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": enhanced_context}
            ],
            model=DEFAULT_MODEL,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate result
        result.setdefault("confidence", 0.5)
        result.setdefault("action_type", "unknown")
        result.setdefault("actions", [])
        result.setdefault("goals_update", [])
        
        logger.info(f"Decision - Type: {result.get('action_type')}, Confidence: {result.get('confidence')}")
        metrics.record_metric("decision_confidence", result.get('confidence', 0))
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        metrics.increment_counter("decision_parse_failed")
        return {
            "analysis": "Error parsing response",
            "action_type": "error",
            "actions": [],
            "goals_update": [],
            "confidence": 0.0
        }
    except Exception as e:
        logger.error(f"Error in decide_action: {e}")
        metrics.increment_counter("decision_failed")
        return {
            "analysis": str(e),
            "action_type": "error",
            "actions": [],
            "goals_update": [],
            "confidence": 0.0
        }

def initialize_jarvis() -> tuple[List[str], List[str]]:
    """Initialize Jarvis with memory and goals."""
    memory = ["Jarvis initialized with full module integration"]
    goals = [
        "Analyze own code structure and dependencies",
        "Identify architectural improvements",
        "Implement self-refactoring capabilities",
        "Create robust error handling",
        "Establish reflection loop"
    ]
    return memory, goals

def run_jarvis_loop(iterations: int = 5):
    """Main autonomous loop for Jarvis."""
    memory, goals = initialize_jarvis()
    
    for i in range(iterations):
        logger.info(f"--- Jarvis Iteration {i+1} ---")
        
        context = f"Iteration {i+1}: Review and improve agent.py. Current goals: {goals}"
        decision = decide_action(context, memory, goals)
        
        memory.append(decision.get("analysis", ""))
        goals.extend(decision.get("goals_update", []))
        
        logger.info(f"Actions: {decision.get('actions', [])}")
        
    logger.info("Jarvis cycle complete")

if __name__ == "__main__":
    run_jarvis_loop(iterations=3)
