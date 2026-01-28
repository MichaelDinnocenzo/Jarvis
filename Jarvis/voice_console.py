"""Voice-activated console for Jarvis self-rewriting."""

import logging
import sys
from typing import Optional
from interface import JarvisInterface
from coder import Coder
from executor import Executor
from permissions import PermissionManager
from memory import MemoryManager
from commands import CommandExecutor

# Optional voice import
try:
    from voice import VoiceInterface
    VOICE_AVAILABLE = True
except ImportError:
    VoiceInterface = None
    VOICE_AVAILABLE = False

logger = logging.getLogger(__name__)

class VoiceConsole:
    """Voice-activated console."""
    
    def __init__(self):
        self.interface = JarvisInterface()
        self.coder = Coder()
        self.executor = Executor()
        self.permissions = PermissionManager()
        self.memory = MemoryManager()
        self.command_executor = CommandExecutor()
        self.voice = VoiceInterface() if VOICE_AVAILABLE else None
        self.running = False
        self.input_mode = "text"  # "text" or "voice"
        
    def start(self):
        """Start voice console."""
        print("\n" + "="*80)
        print("🎤 JARVIS VOICE CONSOLE - SELF-REWRITING MODE")
        print("="*80)
        print("\nHow to use:")
        print("  Say: 'Jarvis, open teams'")
        print("  Say: 'Jarvis, make a calculator app'")
        print("  Say: 'Jarvis, generate a file parser'")
        print("  Say: 'Jarvis, help'")
        print("  Say: 'Jarvis, exit'")
        print("\nInput modes:")
        print("  Type: 'voice' to switch to voice input")
        print("  Type: 'text' to switch to text input")
        print("\n" + "="*80 + "\n")
        
        self.running = True
        while self.running:
            try:
                if self.input_mode == "voice" and self.voice:
                    user_input = self._get_voice_input()
                else:
                    user_input = self._get_text_input()
                
                if not user_input:
                    continue
                
                # Remove "Jarvis, " prefix if present
                if user_input.lower().startswith("jarvis, "):
                    user_input = user_input[8:].strip()
                elif user_input.lower().startswith("jarvis "):
                    user_input = user_input[7:].strip()
                
                # Process command
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Jarvis shutting down...")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}\n")
                logger.error(f"Console error: {e}", exc_info=True)
    
    def _get_text_input(self) -> Optional[str]:
        """Get text input from user."""
        try:
            user_input = input("You (text): ").strip()
            return user_input
        except EOFError:
            return None
    
    def _get_voice_input(self) -> Optional[str]:
        """Get voice input from user."""
        try:
            print("🎤 Listening... (say 'switch to text' to change mode)")
            text = self.voice.listen()
            if text:
                print(f"You (voice): {text}")
                return text
            else:
                print("❌ No speech detected")
                return None
        except Exception as e:
            print(f"❌ Voice input error: {e}")
            logger.error(f"Voice input failed: {e}")
            return None
    
    def _process_command(self, command: str):
        """Process voice/text command."""
        command_lower = command.lower()
        
        # Control commands
        if command_lower == "exit":
            print("Jarvis: 👋 Goodbye!\n")
            self.running = False
            return
        
        if command_lower == "help":
            self._print_help()
            return
        
        if command_lower == "list commands":
            self.interface._print_commands()
            return
        
        if command_lower == "stats":
            self._print_stats()
            return
        
        # Input mode switching
        if command_lower in ["switch to voice", "voice mode", "voice input"]:
            if self.voice:
                self.input_mode = "voice"
                print("Jarvis: 🎤 Switched to voice input mode\n")
            else:
                print("Jarvis: ❌ Voice input not available\n")
            return
        
        if command_lower in ["switch to text", "text mode", "text input"]:
            self.input_mode = "text"
            print("Jarvis: ⌨️  Switched to text input mode\n")
            return
        
        # Check if it's a simple command
        result = self.command_executor.execute_command(command)
        if result.get("success"):
            print(f"Jarvis: ✅ {result['output']}\n")
            return
        
        # Otherwise, generate new code to do it
        print(f"Jarvis: 🔧 Analyzing request: '{command}'")
        print("Jarvis: 💻 Generating code to handle this...\n")
        
        self._self_rewrite_for_command(command)
    
    def _self_rewrite_for_command(self, command: str):
        """Generate and execute code for command."""
        try:
            # Step 1: Generate code
            print("Jarvis: 📝 Step 1: Generating code...")
            specification = f"""
Create a Python function to handle this request:
"{command}"

The function should:
- Be named 'execute_task'
- Take no parameters
- Print what it's doing
- Return success status
- Include error handling

Make it self-contained and executable.
"""
            
            code = self.coder.generate(specification, language="python")
            print(f"Jarvis: ✅ Code generated ({len(code)} chars)")
            print("Jarvis: 📋 Code:\n")
            print(code)
            print()
            
            # Step 2: Validate
            print("Jarvis: 🔐 Step 2: Validating safety...")
            if not self.permissions.check_code_safety(code):
                print("Jarvis: ⚠️  Code blocked by safety checks")
                self.memory.add("security_blocked", f"Blocked: {command}")
                return
            print("Jarvis: ✅ Safety validation passed")
            
            # Step 3: Syntax check
            print("Jarvis: 🔍 Step 3: Checking syntax...")
            if not self.executor.validate(code):
                print("Jarvis: ❌ Syntax errors found")
                return
            print("Jarvis: ✅ Syntax valid")
            
            # Step 4: Test run (dry-run)
            print("Jarvis: 🧪 Step 4: Testing (dry-run)...")
            test_result = self.executor.execute(code, dry_run=True)
            if test_result.get("success"):
                print("Jarvis: ✅ Test passed")
            else:
                print(f"Jarvis: ⚠️  Test warning: {test_result.get('error')}")
            
            # Step 5: Execute
            print("Jarvis: ▶️  Step 5: Executing...")
            result = self.executor.execute(code)
            
            if result.get("success"):
                print(f"Jarvis: ✅ Success!\n")
                if result.get("output"):
                    print(f"Output:\n{result['output']}\n")
                self.memory.add("self_rewrite_success", command)
            else:
                print(f"Jarvis: ❌ Execution failed\n")
                if result.get("error"):
                    print(f"Error: {result['error']}\n")
                self.memory.add("self_rewrite_failed", command)
            
        except Exception as e:
            print(f"Jarvis: ❌ Error: {e}\n")
            logger.error(f"Self-rewrite failed: {e}", exc_info=True)
            self.memory.add("self_rewrite_error", str(e))
    
    def _print_help(self):
        """Print help."""
        print("""
Jarvis: 📖 VOICE CONSOLE HELP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:

📱 Built-in Commands:
  "open teams"              Open Microsoft Teams
  "open vscode"             Open VS Code
  "open discord"            Open Discord
  "open chrome"             Open Chrome
  "open explorer"           Open File Explorer

🤖 Self-Rewriting Commands:
  "make a calculator"       Generate and run calculator code
  "create a file parser"    Generate file parsing code
  "build a web scraper"     Generate web scraping code

🎤 Input Modes:
  "switch to voice"         Switch to voice input
  "switch to text"          Switch to text input

⚙️  Control:
  "help"                    Show this help
  "list commands"           Show built-in commands
  "stats"                   Show statistics
  "exit"                    Exit console

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    def _print_stats(self):
        """Print statistics."""
        stats = self.interface.get_stats()
        print(f"""
Jarvis: 📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Commands Executed: {stats.get('total_executions', 0)}
Successful: {stats.get('successful', 0)}
Failed: {stats.get('failed', 0)}
Input Mode: {self.input_mode}
Voice Available: {'Yes' if VOICE_AVAILABLE else 'No'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
