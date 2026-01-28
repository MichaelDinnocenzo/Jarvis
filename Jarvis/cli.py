"""Command-line interface launcher."""

import sys
import argparse
import logging

from setup import setup_environment
if not setup_environment():
    sys.exit(1)

from logger_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Jarvis - Autonomous AI Software Engineer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py run                    Run Jarvis auto-coding
  python cli.py run --iterations 5     Run with 5 iterations
  python cli.py cmd                    Command interface
  python cli.py help                   Show this help
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run Jarvis autonomous coding")
    run_parser.add_argument("--iterations", type=int, default=3, help="Number of iterations")
    run_parser.add_argument("--auto", action="store_true", help="Auto-execute generated code")
    
    # Command interface
    subparsers.add_parser("cmd", help="Interactive command interface")
    
    # Demo
    subparsers.add_parser("demo", help="Run demo")
    
    # Help
    subparsers.add_parser("help", help="Show help")
    
    args = parser.parse_args()
    
    if args.command == "run":
        _run_jarvis(args.iterations, args.auto)
    elif args.command == "cmd":
        _run_command_interface()
    elif args.command == "demo":
        _run_demo()
    else:
        parser.print_help()

def _run_jarvis(iterations: int, auto_mode: bool):
    """Run Jarvis."""
    try:
        from jarvis import Jarvis
        jarvis = Jarvis()
        jarvis.run(iterations=iterations, auto_mode=auto_mode)
    except Exception as e:
        logger.error(f"Jarvis failed: {e}", exc_info=True)
        sys.exit(1)

def _run_command_interface():
    """Run command interface."""
    try:
        from interface import JarvisInterface
        interface = JarvisInterface()
        interface.interactive_mode()
    except Exception as e:
        logger.error(f"Interface failed: {e}", exc_info=True)
        sys.exit(1)

def _run_demo():
    """Run demo."""
    try:
        import demo
        demo.main()
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
