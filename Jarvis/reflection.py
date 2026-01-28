from permissions import can_modify
import logging
import json
from typing import Dict, List, Any
from api_client import get_api_client
from utils import measure_time, retry
from metrics import get_metrics
from exceptions import ReflectionError
from constants import ACTION_REFLECTION, REFLECTION_DEPTH

logger = logging.getLogger(__name__)
metrics = get_metrics()

class Reflector:
    """Self-reflection and analysis."""
    
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.api_client = get_api_client()
        self.model = "gpt-4o-mini"
        self.reflection_count = 0
        
    @retry(max_attempts=2, delay=1.0)
    @measure_time
    def analyze(self) -> str:
        """Analyze past decisions and performance."""
        recent_decisions = self.memory.get_by_type("decision")[-10:]
        past_actions = self.memory.get_by_type("code_generated")[-5:]
        
        prompt = f"""
Analyze Jarvis performance and provide insights:

Recent Decisions (last 10):
{json.dumps([d['content'] for d in recent_decisions], indent=2)[:1000]}

Recent Actions (last 5):
{json.dumps([a['content'] for a in past_actions], indent=2)[:1000]}

Provide:
1. What worked well
2. What needs improvement
3. Recommended changes
4. Next priorities
Keep response concise (200 words max).
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            insights = response.choices[0].message.content
            self.reflection_count += 1
            metrics.increment_counter("reflections")
            logger.info("Reflection complete")
            return insights
            
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            metrics.increment_counter("reflection_failed")
            raise ReflectionError(f"Reflection failed: {e}")
    
    @retry(max_attempts=2, delay=1.0)
    @measure_time
    def identify_improvements(self) -> List[str]:
        """Identify specific improvements."""
        prompt = f"""
Based on autonomous coding best practices and the reflection depth of {REFLECTION_DEPTH},
provide exactly 3-5 specific, actionable improvements for Jarvis.
Return as JSON array of strings only.
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            improvements = json.loads(response.choices[0].message.content)
            logger.info(f"Identified {len(improvements)} improvements")
            return improvements
            
        except json.JSONDecodeError:
            logger.error("Failed to parse improvements")
            return []
        except Exception as e:
            logger.error(f"Improvement identification failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get reflection statistics."""
        return {"reflections": self.reflection_count}

def reflect(memory, goals):
    # Trim memory
    if len(memory.short) > 8:
        memory.short = memory.short[-4:]

    # Autonomous refactor decision
    for goal in goals.get_active_goals():
        if "architecture" in goal["goal"].lower():
            file = "agent.py"
            if can_modify(file):
                coder.modify(
                    file,
                    "Refactor for clearer decision logic and modularity"
                )
                goals.complete_goal(goal["goal"])
