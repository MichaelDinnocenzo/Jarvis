import json
import logging
import re
from typing import List, Dict
from constants import SAFETY_MODE, BLOCK_DANGEROUS_CODE

logger = logging.getLogger(__name__)

class PermissionManager:
    """Manage code safety and permissions."""
    
    DANGEROUS_PATTERNS = [
        r'__import__',
        r'eval\(',
        r'exec\(',
        r'compile\(',
        r'os\.system',
        r'subprocess\.call',
        r'open\(["\']',
        r'rm\s+-rf',
        r'del\s+',
    ]
    
    RESTRICTED_PATHS = [
        '/etc', '/sys', '/proc', '/root',
        'C:\\Windows\\System32', 'C:\\Windows\\drivers'
    ]
    
    def __init__(self):
        self.blocked_count = 0
        self.allowed_count = 0
        self.warnings = []
        
    def check_code_safety(self, code: str) -> bool:
        """Check if code is safe to execute."""
        if not SAFETY_MODE:
            return True
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                warning = f"Dangerous pattern detected: {pattern}"
                logger.warning(warning)
                self.warnings.append(warning)
                self.blocked_count += 1
                return not BLOCK_DANGEROUS_CODE
        
        self.allowed_count += 1
        return True
    
    def check_file_access(self, filepath: str) -> bool:
        """Check if file access is allowed."""
        for path in self.RESTRICTED_PATHS:
            if filepath.startswith(path):
                warning = f"Restricted path: {filepath}"
                logger.warning(warning)
                self.warnings.append(warning)
                return False
        return True
    
    def check_import_safety(self, module: str) -> bool:
        """Check if module import is safe."""
        dangerous_modules = ['os', 'subprocess', 'ctypes', '__main__']
        if module in dangerous_modules:
            logger.warning(f"Dangerous module import: {module}")
            return False
        return True
    
    def get_stats(self) -> Dict:
        """Get safety stats."""
        total = self.blocked_count + self.allowed_count
        return {
            "blocked": self.blocked_count,
            "allowed": self.allowed_count,
            "total": total,
            "block_rate": f"{(self.blocked_count/total*100):.1f}%" if total > 0 else "0%",
            "recent_warnings": self.warnings[-10:]
        }

with open("config.json") as f:
    config = json.load(f)

def can_modify(file):
    return file not in config["protected_files"]
