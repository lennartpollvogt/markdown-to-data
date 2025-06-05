"""
Configuration and constants for markdown-to-data CLI tool.

This module defines constants, default values, and configuration settings
used across all CLI commands for consistent behavior.
"""

from typing import List, Dict, Any
from enum import Enum


# Version and Package Information
CLI_NAME = "m2d"
CLI_DESCRIPTION = "Convert markdown files to structured data formats and perform various operations"


# File Extensions
MARKDOWN_EXTENSIONS = ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']
JSON_EXTENSION = '.json'
TEXT_EXTENSION = '.txt'


# Default Values
DEFAULT_JSON_INDENT = 2
DEFAULT_SPACER = 1
DEFAULT_MAX_TREE_DEPTH = 10
DEFAULT_BATCH_PATTERN = "**/*.md"


# Output Formats
class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    LIST = "list"
    DICT = "dict"
    MARKDOWN = "markdown"
    TREE = "tree"
    TABLE = "table"


# Element Types (matching the library's element types)
SUPPORTED_ELEMENT_TYPES = [
    'metadata',
    'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'paragraph',
    'list',
    'table',
    'code',
    'blockquote',
    'def_list',
    'separator'
]

# Header types for convenience
HEADER_TYPES = ['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'headers']


# Error Exit Codes
class ExitCode(Enum):
    """Standard exit codes for CLI operations."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    FILE_NOT_FOUND = 2
    INVALID_FILE = 3
    PROCESSING_ERROR = 4
    VALIDATION_ERROR = 5
    BATCH_PROCESSING_ERROR = 6
    PERMISSION_ERROR = 7
    KEYBOARD_INTERRUPT = 130


# Error Messages
ERROR_MESSAGES = {
    'file_not_found': "File not found: {filepath}",
    'invalid_file': "Invalid file '{filepath}': {reason}",
    'processing_error': "Failed to {operation} '{filepath}': {reason}",
    'validation_error': "Invalid {parameter} '{value}': {reason}",
    'batch_error': "Batch processing failed for {failed_count}/{total_files} files",
    'permission_denied': "Permission denied: {filepath}",
    'invalid_json': "Invalid JSON format in '{filepath}': {reason}",
    'output_exists': "Output file already exists: {filepath} (use --overwrite to replace)",
    'no_files_found': "No files found matching pattern: {pattern}",
    'invalid_element_type': "Invalid element type '{element_type}'. Supported types: {supported_types}",
    'conflicting_options': "Conflicting options: {option1} and {option2} cannot be used together",
}


# Success Messages
SUCCESS_MESSAGES = {
    'file_processed': "Successfully processed: {filepath}",
    'batch_completed': "Batch processing completed: {successful}/{total_files} files successful",
    'output_written': "Output written to: {output_path}",
    'conversion_complete': "Conversion completed successfully",
    'extraction_complete': "Extraction completed successfully",
    'info_extracted': "Information extracted successfully",
}


# Warning Messages
WARNING_MESSAGES = {
    'no_metadata': "No metadata found in file: {filepath}",
    'empty_file': "File is empty: {filepath}",
    'no_elements': "No elements of type '{element_type}' found in: {filepath}",
    'partial_failure': "Some files failed processing, check error messages above",
    'large_file': "Large file detected ({size}), processing may take longer: {filepath}",
    'overwriting_file': "Overwriting existing file: {filepath}",
}


# Help Text Templates
HELP_TEXT = {
    'input_file': "Path to input markdown file",
    'input_pattern': "Pattern to match input files (supports glob patterns)",
    'output_file': "Path to output file (optional, defaults to input filename with different extension)",
    'output_dir': "Directory for output files",
    'format': f"Output format: {', '.join([f.value for f in OutputFormat])}",
    'indent': "JSON indentation level (0 for compact)",
    'overwrite': "Overwrite existing output files",
    'recursive': "Search for files recursively",
    'verbose': "Enable verbose output",
    'quiet': "Suppress non-error output",
    'include': f"Element types to include. Supported: {', '.join(SUPPORTED_ELEMENT_TYPES)}",
    'exclude': f"Element types to exclude. Supported: {', '.join(SUPPORTED_ELEMENT_TYPES)}",
    'spacer': "Number of empty lines between elements when converting to markdown",
    'max_depth': "Maximum depth for tree display",
    'compact': "Use compact output format",
    'batch': "Process multiple files",
}


# Command Descriptions
COMMAND_DESCRIPTIONS = {
    'info': "Extract metadata and structural information from markdown files",
    'batch-info': "Extract information from multiple markdown files",
    'convert': "Convert markdown files to JSON format",
    'batch-convert': "Convert multiple markdown files to JSON format",
    'extract': "Extract specific elements from markdown files",
    'batch-extract': "Extract elements from multiple markdown files",
    'md': "Convert JSON data back to markdown format",
    'batch-md': "Convert multiple JSON files back to markdown format",
    'tree': "Display markdown structure as a tree",
    'search': "Search for content within markdown files",
}


# Batch Processing Settings
BATCH_SETTINGS = {
    'max_files_warning': 100,  # Warn if processing more than this many files
    'progress_threshold': 5,   # Show progress bar if more than this many files
    'chunk_size': 50,          # Process files in chunks of this size
    'max_workers': 4,          # Maximum number of worker threads
}


# Display Settings
DISPLAY_SETTINGS = {
    'max_content_preview': 50,     # Maximum characters to show in content preview
    'max_list_items_preview': 5,   # Maximum list items to show in tree view
    'table_max_width': 120,        # Maximum table width in terminal
    'tree_max_depth_default': 5,   # Default maximum tree depth
}


# File Size Limits (in bytes)
FILE_SIZE_LIMITS = {
    'warning_threshold': 1024 * 1024,      # 1MB - warn for files larger than this
    'max_file_size': 10 * 1024 * 1024,     # 10MB - refuse to process files larger than this
}


# Search Settings
SEARCH_SETTINGS = {
    'max_results': 100,           # Maximum search results to display
    'context_lines': 2,           # Lines of context around search matches
    'highlight_color': 'yellow',  # Color for highlighting search matches
}


# Default Exclude Patterns for Batch Processing
DEFAULT_EXCLUDE_PATTERNS = [
    '*.tmp',
    '*.bak',
    '*.swp',
    '*~',
    '.git/**',
    '.svn/**',
    '.hg/**',
    'node_modules/**',
    '__pycache__/**',
    '.vscode/**',
    '.idea/**',
]


# Validation Rules
VALIDATION_RULES = {
    'max_filename_length': 255,
    'max_path_length': 4096,
    'min_indent': 0,
    'max_indent': 8,
    'min_spacer': 0,
    'max_spacer': 10,
    'min_depth': 1,
    'max_depth': 20,
}


# Rich Theme Settings
RICH_THEME = {
    'error': 'bold red',
    'warning': 'bold yellow',
    'success': 'bold green',
    'info': 'cyan',
    'verbose': 'dim cyan',
    'filename': 'blue',
    'element': 'magenta',
    'count': 'green',
    'metadata': 'yellow',
}


# CLI Options Common to Multiple Commands
COMMON_OPTIONS = {
    'verbose': {
        'short': '-v',
        'long': '--verbose',
        'help': HELP_TEXT['verbose'],
        'is_flag': True,
    },
    'quiet': {
        'short': '-q',
        'long': '--quiet',
        'help': HELP_TEXT['quiet'],
        'is_flag': True,
    },
    'overwrite': {
        'long': '--overwrite',
        'help': HELP_TEXT['overwrite'],
        'is_flag': True,
    },
    'output': {
        'short': '-o',
        'long': '--output',
        'help': HELP_TEXT['output_file'],
        'type': str,
    },
    'format': {
        'short': '-f',
        'long': '--format',
        'help': HELP_TEXT['format'],
        'type': str,
        'default': OutputFormat.JSON.value,
    },
    'indent': {
        'long': '--indent',
        'help': HELP_TEXT['indent'],
        'type': int,
        'default': DEFAULT_JSON_INDENT,
    },
    'compact': {
        'long': '--compact',
        'help': HELP_TEXT['compact'],
        'is_flag': True,
    },
}


# Batch-specific options
BATCH_OPTIONS = {
    'recursive': {
        'short': '-r',
        'long': '--recursive',
        'help': HELP_TEXT['recursive'],
        'is_flag': True,
        'default': True,
    },
    'output_dir': {
        'long': '--output-dir',
        'help': HELP_TEXT['output_dir'],
        'type': str,
    },
    'exclude': {
        'long': '--exclude',
        'help': 'Patterns to exclude from processing',
        'multiple': True,
        'type': str,
    },
}


def get_version() -> str:
    """Get the current version of the package."""
    try:
        from importlib.metadata import version
        return version('markdown-to-data')
    except ImportError:
        # Fallback for Python < 3.8
        try:
            from importlib_metadata import version
            return version('markdown-to-data')
        except ImportError:
            return "unknown"


def validate_element_type(element_type: str) -> bool:
    """
    Validate if an element type is supported.
    
    Args:
        element_type: Element type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return element_type in SUPPORTED_ELEMENT_TYPES


def get_supported_element_types_string() -> str:
    """
    Get a formatted string of supported element types.
    
    Returns:
        Comma-separated string of supported element types
    """
    return ', '.join(SUPPORTED_ELEMENT_TYPES)


def get_markdown_extensions_pattern() -> str:
    """
    Get a glob pattern for all supported markdown extensions.
    
    Returns:
        Glob pattern string
    """
    return '{' + ','.join([f'*{ext}' for ext in MARKDOWN_EXTENSIONS]) + '}'


# Configuration class for runtime settings
class CLIConfig:
    """Runtime configuration for CLI operations."""
    
    def __init__(self):
        self.verbose: bool = False
        self.quiet: bool = False
        self.overwrite: bool = False
        self.max_workers: int = BATCH_SETTINGS['max_workers']
        self.chunk_size: int = BATCH_SETTINGS['chunk_size']
        self.progress_threshold: int = BATCH_SETTINGS['progress_threshold']
    
    def update_from_context(self, ctx_obj: Dict[str, Any]) -> None:
        """Update configuration from click context object."""
        self.verbose = ctx_obj.get('verbose', False)
        self.quiet = ctx_obj.get('quiet', False)
        self.overwrite = ctx_obj.get('overwrite', False)
    
    def should_show_progress(self, file_count: int) -> bool:
        """Determine if progress bar should be shown."""
        return file_count >= self.progress_threshold and not self.quiet


# Global configuration instance
cli_config = CLIConfig()