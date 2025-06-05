"""
Error handling utilities for markdown-to-data CLI tool.

This module provides custom exceptions and error handling functions
for consistent error management across all CLI commands.
"""

import sys
from typing import Optional, Any
import click
from rich.console import Console
from rich.text import Text

console = Console(stderr=True)


class CLIError(Exception):
    """Base exception for CLI-related errors."""
    
    def __init__(self, message: str, exit_code: int = 1, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details


class FileNotFoundError(CLIError):
    """Raised when a required file is not found."""
    
    def __init__(self, filepath: str, details: Optional[str] = None):
        message = f"File not found: {filepath}"
        super().__init__(message, exit_code=2, details=details)
        self.filepath = filepath


class InvalidFileError(CLIError):
    """Raised when a file is invalid or corrupted."""
    
    def __init__(self, filepath: str, reason: str, details: Optional[str] = None):
        message = f"Invalid file '{filepath}': {reason}"
        super().__init__(message, exit_code=3, details=details)
        self.filepath = filepath
        self.reason = reason


class ProcessingError(CLIError):
    """Raised when processing a file fails."""
    
    def __init__(self, filepath: str, operation: str, reason: str, details: Optional[str] = None):
        message = f"Failed to {operation} '{filepath}': {reason}"
        super().__init__(message, exit_code=4, details=details)
        self.filepath = filepath
        self.operation = operation
        self.reason = reason


class ValidationError(CLIError):
    """Raised when input validation fails."""
    
    def __init__(self, parameter: str, value: Any, reason: str, details: Optional[str] = None):
        message = f"Invalid {parameter} '{value}': {reason}"
        super().__init__(message, exit_code=5, details=details)
        self.parameter = parameter
        self.value = value
        self.reason = reason


class BatchProcessingError(CLIError):
    """Raised when batch processing encounters errors."""
    
    def __init__(self, failed_files: list, total_files: int, details: Optional[str] = None):
        failed_count = len(failed_files)
        message = f"Batch processing failed for {failed_count}/{total_files} files"
        super().__init__(message, exit_code=6, details=details)
        self.failed_files = failed_files
        self.total_files = total_files
        self.failed_count = failed_count


def handle_cli_error(error: CLIError, verbose: bool = False) -> None:
    """
    Handle CLI errors with consistent formatting and appropriate exit codes.
    
    Args:
        error: The CLI error to handle
        verbose: Whether to show detailed error information
    """
    # Create error message with rich formatting
    error_text = Text()
    error_text.append("Error: ", style="bold red")
    error_text.append(error.message, style="red")
    
    console.print(error_text)
    
    # Show details if available and verbose mode is enabled
    if verbose and error.details:
        console.print(f"Details: {error.details}", style="dim red")
    
    # Show suggestions based on error type
    if isinstance(error, FileNotFoundError):
        console.print("💡 Check if the file path is correct and the file exists.", style="dim yellow")
    elif isinstance(error, InvalidFileError):
        console.print("💡 Ensure the file is a valid markdown file and not corrupted.", style="dim yellow")
    elif isinstance(error, ProcessingError):
        console.print("💡 Try with a different file or check the file content.", style="dim yellow")
    elif isinstance(error, ValidationError):
        console.print("💡 Check the command usage with --help for valid parameters.", style="dim yellow")
    elif isinstance(error, BatchProcessingError):
        console.print("💡 Use --verbose to see details about failed files.", style="dim yellow")
    
    sys.exit(error.exit_code)


def handle_unexpected_error(error: Exception, verbose: bool = False) -> None:
    """
    Handle unexpected errors with proper formatting.
    
    Args:
        error: The unexpected error
        verbose: Whether to show detailed error information
    """
    error_text = Text()
    error_text.append("Unexpected Error: ", style="bold red")
    error_text.append(str(error), style="red")
    
    console.print(error_text)
    
    if verbose:
        console.print_exception()
    else:
        console.print("💡 Use --verbose for more details.", style="dim yellow")
    
    sys.exit(1)


def validate_file_exists(filepath: str) -> None:
    """
    Validate that a file exists.
    
    Args:
        filepath: Path to the file to validate
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    import os
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    
    if not os.path.isfile(filepath):
        raise InvalidFileError(filepath, "Path is not a file")


def validate_markdown_file(filepath: str) -> None:
    """
    Validate that a file is a markdown file.
    
    Args:
        filepath: Path to the file to validate
        
    Raises:
        InvalidFileError: If the file is not a valid markdown file
    """
    import os
    
    # Check if file exists first
    validate_file_exists(filepath)
    
    # Check file extension
    valid_extensions = ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']
    _, ext = os.path.splitext(filepath.lower())
    
    if ext not in valid_extensions:
        raise InvalidFileError(
            filepath, 
            f"Not a markdown file (expected extensions: {', '.join(valid_extensions)})"
        )
    
    # Check if file is readable
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1)  # Try to read first character
    except UnicodeDecodeError:
        raise InvalidFileError(filepath, "File contains invalid UTF-8 encoding")
    except PermissionError:
        raise InvalidFileError(filepath, "Permission denied")
    except Exception as e:
        raise InvalidFileError(filepath, f"Cannot read file: {str(e)}")


def validate_json_file(filepath: str) -> None:
    """
    Validate that a file is a JSON file.
    
    Args:
        filepath: Path to the file to validate
        
    Raises:
        InvalidFileError: If the file is not a valid JSON file
    """
    import os
    import json
    
    # Check if file exists first
    validate_file_exists(filepath)
    
    # Check file extension
    if not filepath.lower().endswith('.json'):
        raise InvalidFileError(filepath, "Not a JSON file (expected .json extension)")
    
    # Check if file contains valid JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise InvalidFileError(filepath, f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise InvalidFileError(filepath, f"Cannot read JSON file: {str(e)}")


def safe_operation(operation_name: str, filepath: str = None):
    """
    Decorator to safely execute operations with proper error handling.
    
    Args:
        operation_name: Name of the operation being performed
        filepath: Optional filepath being processed
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CLIError:
                # Re-raise CLI errors as-is
                raise
            except Exception as e:
                # Convert unexpected errors to ProcessingError
                if filepath:
                    raise ProcessingError(filepath, operation_name, str(e))
                else:
                    raise CLIError(f"Failed to {operation_name}: {str(e)}")
        return wrapper
    return decorator