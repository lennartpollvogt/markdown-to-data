#!/usr/bin/env python3
"""
Test script for markdown-to-data CLI tool.

This script makes it easy to test the CLI tool during development
without having to type long Python commands.

Usage:
    python test_cli.py [command] [args...]
    
Examples:
    python test_cli.py --help
    python test_cli.py info --help
    python test_cli.py convert --help
    python test_cli.py info README.md
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from markdown_to_data.cli_tool.main import cli
except ImportError as e:
    print(f"Error importing CLI: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def main():
    """Run the CLI with provided arguments."""
    try:
        # If no arguments provided, show help
        if len(sys.argv) == 1:
            cli(['--help'])
        else:
            # Pass all arguments except the script name
            cli(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()