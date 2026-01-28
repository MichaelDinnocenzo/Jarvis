import logging
import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from utils import measure_time, retry
from metrics import get_metrics
from exceptions import CodeExecutionError
from constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)
metrics = get_metrics()

class Executor:
    """Safely execute code."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.execution_history = []
        self.execution_count = 0
        self.success_count = 0
        
    @measure_time
    def execute(self, code: str, language: str = "python", dry_run: bool = False) -> Dict[str, Any]:
        """Execute code safely."""
        self.execution_count += 1
        
        if dry_run:
            logger.info(f"DRY RUN: Would execute {len(code)} chars of {language}")
            metrics.increment_counter("dry_runs")
            return {"success": True, "output": "", "dry_run": True, "error": ""}
        
        # Validate code first
        if language == "python" and not self.validate(code):
            logger.error("Code validation failed")
            raise CodeExecutionError("Code validation failed")
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    [language, temp_file],
                    capture_output=True,
                    timeout=self.timeout,
                    text=True,
                    cwd=Path.cwd()
                )
                
                output = {
                    "success": result.returncode == 0,
                    "output": result.stdout[:5000],
                    "error": result.stderr[:5000],
                    "return_code": result.returncode,
                    "dry_run": False
                }
                
                if output["success"]:
                    self.success_count += 1
                    metrics.increment_counter("execution_success")
                else:
                    metrics.increment_counter("execution_failed")
                
                self.execution_history.append(output)
                logger.info(f"Execution {'successful' if output['success'] else 'failed'}")
                return output
                
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                
        except subprocess.TimeoutExpired:
            logger.error(f"Execution timeout ({self.timeout}s)")
            metrics.increment_counter("execution_timeout")
            return {"success": False, "output": "", "error": f"Timeout after {self.timeout}s", "return_code": -1, "dry_run": False}
        except Exception as e:
            logger.error(f"Execution error: {e}")
            metrics.increment_counter("execution_error")
            return {"success": False, "output": "", "error": str(e), "return_code": -1, "dry_run": False}
    
    def validate(self, code: str) -> bool:
        """Validate code syntax."""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get execution statistics."""
        success_rate = (self.success_count / self.execution_count * 100) if self.execution_count > 0 else 0
        return {
            "total_executions": self.execution_count,
            "successful": self.success_count,
            "failed": self.execution_count - self.success_count,
            "success_rate": f"{success_rate:.1f}%"
        }
