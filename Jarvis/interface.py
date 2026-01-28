"""User interface for Jarvis commands."""

import logging
from typing import Optional
from commands import CommandExecutor

logger = logging.getLogger(__name__)

class JarvisInterface:
    """Interactive interface for Jarvis."""
    
    def __init__(self):
        self.executor = CommandExecutor()
        self.running = False
    
    def interactive_mode(self):
        """Run interactive command mode."""
        print("\n" + "="*80)
        print("JARVIS COMMAND INTERFACE")
        print("="*80)
        print("\nAvailable commands:")
        self._print_commands()
        print("\nType 'help' for more options")
        print("Type 'quit' or 'exit' to stop\n")
        
        self.running = True
        while self.running:
            try:
                user_input = input("Jarvis> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    print("\n👋 Goodbye!")
                    self.running = False
                    break
                
                if user_input.lower() == "help":
                    self._print_help()
                    continue
                
                if user_input.lower() == "list":
                    self._print_commands()
                    continue
                
                if user_input.lower().startswith("url "):
                    url = user_input[4:].strip()
                    result = self.executor.open_url(url)
                    print(f"  → {result['output']}\n")
                    continue
                
                if user_input.lower().startswith("file "):
                    file_path = user_input[5:].strip()
                    result = self.executor.open_file(file_path)
                    print(f"  → {result['output']}\n")
                    continue
                
                # Execute command
                result = self.executor.execute_command(user_input)
                print(f"  → {result['output']}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                self.running = False
            except Exception as e:
                print(f"  ❌ Error: {e}\n")
                logger.error(f"Interface error: {e}")
    
    def _print_commands(self):
        """Print available commands."""
        commands = self.executor.get_available_commands()
        
        print("\n📱 Applications:")
        for cmd in commands:
            if cmd["type"] == "application":
                aliases_str = f" ({', '.join(cmd['aliases'])})" if cmd['aliases'] else ""
                print(f"  • {cmd['name']}{aliases_str}")
        
        print("\n⚙️  System:")
        for cmd in commands:
            if cmd["type"] == "system":
                aliases_str = f" ({', '.join(cmd['aliases'])})" if cmd['aliases'] else ""
                print(f"  • {cmd['name']}{aliases_str}")
    
    def _print_help(self):
        """Print help information."""
        print("""
📖 JARVIS COMMAND HELP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:
  open teams              Open Microsoft Teams
  open vscode             Open Visual Studio Code
  open discord            Open Discord
  open chrome             Open Google Chrome
  
  url google.com          Open URL in browser
  file C:\\path\\to\\file  Open file

Control:
  list                    Show all commands
  help                    Show this help
  quit/exit               Exit interface

Examples:
  > open teams
  > url youtube.com
  > file C:\\Users\\Documents\\file.txt
  > open discord
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    def execute(self, command: str) -> dict:
        """Execute command programmatically."""
        return self.executor.execute_command(command)
    
    def get_stats(self) -> dict:
        """Get statistics."""
        return self.executor.get_stats()
