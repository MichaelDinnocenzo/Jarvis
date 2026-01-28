import logging
import json
from typing import Dict, Any
from api_client import get_api_client
from cache import get_cache_manager
from utils import retry, measure_time
from metrics import get_metrics
from exceptions import ResearchError

logger = logging.getLogger(__name__)
cache = get_cache_manager()
metrics = get_metrics()

class Researcher:
    """Research and gather context."""
    
    def __init__(self):
        self.api_client = get_api_client()
        self.model = "gpt-4o-mini"
        self.research_count = 0
        
    @retry(max_attempts=2, delay=1.0)
    @measure_time
    def search(self, query: str) -> str:
        """Search for information."""
        cache_key = f"research_{query[:50]}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Using cached research")
            return cached
        
        prompt = f"""
Research and provide detailed information about:
{query}

Include:
- Background
- Current best practices
- Common patterns
- Recommendations

Keep response concise (300 words max).
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=800
            )
            
            findings = response.choices[0].message.content
            cache.set(cache_key, findings)
            self.research_count += 1
            metrics.increment_counter("research")
            logger.info(f"Research complete for: {query[:40]}...")
            return findings
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            metrics.increment_counter("research_failed")
            raise ResearchError(f"Research failed: {e}")
    
    @retry(max_attempts=2, delay=1.0)
    @measure_time
    def analyze_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """Analyze codebase structure."""
        prompt = f"""
Analyze the codebase at {codebase_path}
Provide JSON with:
- file_count (number)
- main_technologies (list)
- code_quality_estimate (number 0-100)
- architectural_issues (list)
- improvement_opportunities (list)

Respond with ONLY valid JSON.
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.5,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Codebase analysis complete")
            return result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse analysis")
            return {}
        except Exception as e:
            logger.error(f"Codebase analysis failed: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """Get research statistics."""
        return {"research_queries": self.research_count}
