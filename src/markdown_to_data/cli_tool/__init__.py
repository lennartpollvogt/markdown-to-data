"""
CLI tool package for markdown-to-data.

This package provides command-line interface functionality for the markdown-to-data library,
allowing users to perform various operations on markdown files from the terminal.

Note: CLI functionality requires additional dependencies. Install with:
    pip install 'markdown-to-data[cli]'
"""

# Only expose CLI components if dependencies are available
try:
    import click
    import rich
    import psutil
    
    # Import CLI components
    from .main import main
    
    # Try to import cli but handle gracefully if commands fail
    try:
        from .main import setup_and_run_cli
        __all__ = ['main']
    except ImportError:
        # Commands might fail to import, but main should still work
        __all__ = ['main']
        
except ImportError:
    # CLI dependencies not available - provide helpful message
    def main():
        """Entry point that shows installation message when dependencies missing."""
        print("❌ CLI dependencies not found!")
        print()
        print("The markdown-to-data CLI tool requires additional dependencies.")
        print("Please install them using one of these commands:")
        print()
        print("  pip install 'markdown-to-data[cli]'")
        print("  uv add 'markdown-to-data[cli]'")
        print("  pip install markdown-to-data click rich psutil")
        print()
        print("After installation, the 'm2d' command will be available.")
        
    __all__ = ['main']