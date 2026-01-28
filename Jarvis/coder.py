import logging
import json
from typing import Dict, List, Optional
from api_client import get_api_client
from utils import retry, measure_time, truncate
from cache import get_cache_manager
from metrics import get_metrics
from exceptions import CodeGenerationError
from constants import MAX_CODE_LENGTH, MAX_TOKENS

logger = logging.getLogger(__name__)
cache = get_cache_manager()
metrics = get_metrics()

class Coder:
    """Handles code generation and refactoring."""
    
    def __init__(self):
        self.api_client = get_api_client()
        self.model = "gpt-4o-mini"
        self.generation_count = 0
        self.refactor_count = 0
        
    @retry(max_attempts=3, delay=1.0)
    @measure_time
    def generate(self, specification: str, language: str = "python") -> str:
        """Generate code from specification."""
        cache_key = f"gen_{language}_{specification[:50]}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Using cached code generation")
            return cached
        
        prompt = f"""
Generate production-ready {language} code for:
{specification}

Requirements:
- Include error handling
- Add logging
- Type hints (if applicable)
- Docstrings
- Follow best practices
- Keep under {MAX_CODE_LENGTH} characters
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=MAX_TOKENS
            )
            
            code = response.choices[0].message.content
            code = code[:MAX_CODE_LENGTH]
            
            cache.set(cache_key, code)
            self.generation_count += 1
            metrics.increment_counter("code_generated")
            metrics.record_metric("code_generation_length", len(code))
            
            logger.info(f"Generated {len(code)} chars of code")
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            metrics.increment_counter("code_generation_failed")
            raise CodeGenerationError(f"Code generation failed: {e}")
            
    @retry(max_attempts=3, delay=1.0)
    @measure_time
    def refactor(self, code: str, improvements: Optional[List[str]] = None) -> str:
        """Refactor existing code."""
        improvements_str = "\n".join(improvements) if improvements else "General improvements"
        
        prompt = f"""
Refactor this code with improvements:
{improvements_str}

Original code:
```
{code[:2000]}
```

Provide refactored code only, keep under {MAX_CODE_LENGTH} characters.
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=MAX_TOKENS
            )
            
            refactored = response.choices[0].message.content[:MAX_CODE_LENGTH]
            self.refactor_count += 1
            metrics.increment_counter("code_refactored")
            logger.info(f"Refactored code ({len(refactored)} chars)")
            return refactored
            
        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            metrics.increment_counter("code_refactor_failed")
            return code
            
    @retry(max_attempts=2, delay=0.5)
    @measure_time
    def analyze(self, code: str) -> Dict:
        """Analyze code quality."""
        prompt = f"""
Analyze this code and provide JSON with keys:
- quality_score (0-100)
- issues (list of strings)
- improvements (list of strings)
- complexity (low/medium/high)

Code:
```
{code[:2000]}
```

Respond ONLY with valid JSON.
"""
        
        try:
            response = self.api_client.create_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.5,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            metrics.record_metric("code_quality_score", result.get("quality_score", 0))
            logger.info(f"Code analysis: quality={result.get('quality_score')}/100")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Analysis parsing failed: {e}")
            return {"quality_score": 0, "issues": ["Parsing error"], "improvements": [], "complexity": "unknown"}
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"quality_score": 0, "issues": [str(e)], "improvements": [], "complexity": "unknown"}
    
    def get_stats(self) -> Dict:
        """Get coder statistics."""
        return {
            "codes_generated": self.generation_count,
            "codes_refactored": self.refactor_count,
            "total_operations": self.generation_count + self.refactor_count
        }
