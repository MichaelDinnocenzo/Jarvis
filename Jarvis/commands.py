"""Command execution system for Jarvis."""

import logging
import subprocess
import os
from typing import Dict, List, Any, Callable, Optional
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Command types."""
    APPLICATION = "application"
    SYSTEM = "system"
    FILE = "file"
    CUSTOM = "custom"

class Command:
    """Executable command."""
    
    def __init__(self, name: str, cmd_type: CommandType, action: str, aliases: List[str] = None):
        self.name = name
        self.cmd_type = cmd_type
        self.action = action
        self.aliases = aliases or []
    
    def matches(self, query: str) -> bool:
        """Check if command matches query."""
        query_lower = query.lower()
        return (self.name.lower() in query_lower or 
                any(alias.lower() in query_lower for alias in self.aliases))

class CommandExecutor:
    """Execute commands."""
    
    def __init__(self):
        self.commands = self._initialize_commands()
        self.custom_callbacks: Dict[str, Callable] = {}
        self.execution_history = []
    
    def _initialize_commands(self) -> List[Command]:
        """Initialize default commands."""
        return [
            # Applications
            Command("Teams", CommandType.APPLICATION, "cmd /c start teams:", 
                   ["microsoft teams", "teams app"]),
            Command("Discord", CommandType.APPLICATION, "cmd /c start discord:",
                   ["discord app"]),
            Command("Slack", CommandType.APPLICATION, "cmd /c start slack:",
                   ["slack app"]),
            Command("VS Code", CommandType.APPLICATION, "code",
                   ["visual studio code", "vscode", "editor"]),
            Command("Notepad", CommandType.APPLICATION, "notepad",
                   ["text editor", "note"]),
            Command("Explorer", CommandType.APPLICATION, "explorer",
                   ["file explorer", "files"]),
            Command("Chrome", CommandType.APPLICATION, "chrome",
                   ["google chrome", "browser"]),
            Command("Firefox", CommandType.APPLICATION, "firefox",
                   ["firefox browser"]),
            Command("Spotify", CommandType.APPLICATION, "cmd /c start spotify:",
                   ["music", "spotify app"]),
            Command("Calculator", CommandType.APPLICATION, "calc",
                   ["calc", "calculator"]),
            
            # System commands
            Command("Shutdown", CommandType.SYSTEM, "shutdown /s /t 30",
                   ["shutdown", "turn off"]),
            Command("Restart", CommandType.SYSTEM, "shutdown /r /t 30",
                   ["restart", "reboot"]),
            Command("Sleep", CommandType.SYSTEM, "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                   ["sleep", "hibernate"]),
            Command("Lock", CommandType.SYSTEM, "rundll32.exe user32.dll,LockWorkStation",
                   ["lock screen", "lock"]),
            Command("Volume Up", CommandType.SYSTEM, "nircmd.exe changesysvolume 1000",
                   ["increase volume", "louder"]),
            Command("Volume Down", CommandType.SYSTEM, "nircmd.exe changesysvolume -1000",
                   ["decrease volume", "quieter"]),
        ]
    
    def register_command(self, name: str, callback: Callable, aliases: List[str] = None):
        """Register custom command callback."""
        self.custom_callbacks[name.lower()] = callback
        logger.info(f"Command registered: {name}")
    
    def execute_command(self, query: str) -> Dict[str, Any]:
        """Execute command from query."""
        try:
            # Check custom callbacks first
            for cmd_name, callback in self.custom_callbacks.items():
                if cmd_name in query.lower():
                    result = callback(query)
                    self.execution_history.append({
                        "type": "custom",
                        "command": query,
                        "success": True
                    })
                    logger.info(f"Custom command executed: {cmd_name}")
                    return {"success": True, "output": str(result)}
            
            # Check default commands
            for command in self.commands:
                if command.matches(query):
                    return self._execute_system_command(command, query)
            
            logger.warning(f"Command not found: {query}")
            return {"success": False, "output": f"Command not found: {query}"}
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"success": False, "output": str(e)}
    
    def _execute_system_command(self, command: Command, query: str) -> Dict[str, Any]:
        """Execute system command."""
        try:
            if command.cmd_type == CommandType.APPLICATION:
                subprocess.Popen(command.action, shell=True)
                msg = f"Opening {command.name}..."
                logger.info(msg)
                self.execution_history.append({
                    "type": "application",
                    "command": command.name,
                    "success": True
                })
                return {"success": True, "output": msg}
            
            elif command.cmd_type == CommandType.SYSTEM:
                if "shutdown" in command.action.lower() or "restart" in command.action.lower():
                    logger.warning(f"System command requires confirmation: {command.name}")
                    return {"success": False, "output": f"{command.name} requires user confirmation"}
                
                subprocess.run(command.action, shell=True, check=True)
                msg = f"Executed: {command.name}"
                logger.info(msg)
                self.execution_history.append({
                    "type": "system",
                    "command": command.name,
                    "success": True
                })
                return {"success": True, "output": msg}
            
        except Exception as e:
            logger.error(f"System command failed: {e}")
            self.execution_history.append({
                "type": command.cmd_type.value,
                "command": command.name,
                "success": False,
                "error": str(e)
            })
            return {"success": False, "output": str(e)}
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open a file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "output": f"File not found: {file_path}"}
            
            os.startfile(file_path)
            msg = f"Opening {file_path.name}..."
            logger.info(msg)
            return {"success": True, "output": msg}
            
        except Exception as e:
            logger.error(f"File open failed: {e}")
            return {"success": False, "output": str(e)}
    
    def open_url(self, url: str) -> Dict[str, Any]:
        """Open URL in default browser."""
        try:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            
            subprocess.Popen(f'cmd /c start "{url}"', shell=True)
            logger.info(f"Opening URL: {url}")
            return {"success": True, "output": f"Opening {url}..."}
            
        except Exception as e:
            logger.error(f"URL open failed: {e}")
            return {"success": False, "output": str(e)}
    
    def get_available_commands(self) -> List[Dict[str, str]]:
        """Get list of available commands."""
        cmds = []
        for cmd in self.commands:
            cmds.append({
                "name": cmd.name,
                "type": cmd.cmd_type.value,
                "aliases": cmd.aliases
            })
        return cmds
    
    def get_stats(self) -> Dict:
        """Get execution statistics."""
        successful = sum(1 for e in self.execution_history if e.get("success"))
        return {
            "total_executions": len(self.execution_history),
            "successful": successful,
            "failed": len(self.execution_history) - successful
        }
