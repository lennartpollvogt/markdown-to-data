"""
Error handling utilities for markdown-to-data CLI tool.

This module provides custom exceptions and error handling functions
for consistent error management across all CLI commands.
"""

import sys
import logging
from typing import Optional, Any, Dict
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.text import Text
from rich.logging import RichHandler

console = Console(stderr=True)

# Configure enhanced logging
class CLILogger:
    """Enhanced logger for CLI operations with multiple output levels."""
    
    def __init__(self):
        self.logger = logging.getLogger('markdown-to-data-cli')
        self.logger.setLevel(logging.DEBUG)
        
        # Rich handler for console output
        self.rich_handler = RichHandler(
            console=Console(stderr=True),
            show_time=False,
            show_path=False,
            rich_tracebacks=True
        )
        self.rich_handler.setLevel(logging.INFO)
        
        # File handler for detailed logs
        self.file_handler = None
        
        # Add console handler
        if not self.logger.handlers:
            self.logger.addHandler(self.rich_handler)
    
    def set_level(self, level: str) -> None:
        """Set logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        log_level = level_map.get(level.upper(), logging.INFO)
        self.rich_handler.setLevel(log_level)
    
    def enable_file_logging(self, log_file: Optional[str] = None) -> None:
        """Enable logging to file."""
        if not log_file:
            log_file = f"m2d_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
        
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)

# Global logger instance
cli_logger = CLILogger()


class CLIError(Exception):
    """Base exception for CLI-related errors."""
    
    def __init__(self, message: str, exit_code: int = 1, details: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def get_context_info(self) -> str:
        """Get formatted context information."""
        if not self.context:
            return ""
        
        context_parts = []
        for key, value in self.context.items():
            context_parts.append(f"{key}: {value}")
        return " | ".join(context_parts)


class FileNotFoundError(CLIError):
    """Raised when a required file is not found."""
    
    def __init__(self, filepath: str, details: Optional[str] = None):
        message = f"File not found: {filepath}"
        context = {"filepath": filepath, "file_exists": Path(filepath).exists()}
        super().__init__(message, exit_code=2, details=details, context=context)
        self.filepath = filepath


class InvalidFileError(CLIError):
    """Raised when a file is invalid or corrupted."""
    
    def __init__(self, filepath: str, reason: str, details: Optional[str] = None):
        message = f"Invalid file '{filepath}': {reason}"
        context = {
            "filepath": filepath, 
            "reason": reason,
            "file_size": Path(filepath).stat().st_size if Path(filepath).exists() else 0
        }
        super().__init__(message, exit_code=3, details=details, context=context)
        self.filepath = filepath
        self.reason = reason


class ProcessingError(CLIError):
    """Raised when processing a file fails."""
    
    def __init__(self, filepath: str, operation: str, reason: str, details: Optional[str] = None):
        message = f"Failed to {operation} '{filepath}': {reason}"
        context = {
            "filepath": filepath,
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, exit_code=4, details=details, context=context)
        self.filepath = filepath
        self.operation = operation
        self.reason = reason


class ValidationError(CLIError):
    """Raised when input validation fails."""
    
    def __init__(self, parameter: str, value: Any, reason: str, details: Optional[str] = None):
        message = f"Invalid {parameter} '{value}': {reason}"
        context = {
            "parameter": parameter,
            "value": str(value),
            "reason": reason,
            "value_type": type(value).__name__
        }
        super().__init__(message, exit_code=5, details=details, context=context)
        self.parameter = parameter
        self.value = value
        self.reason = reason


class BatchProcessingError(CLIError):
    """Raised when batch processing encounters errors."""
    
    def __init__(self, failed_files: list, total_files: int, details: Optional[str] = None):
        failed_count = len(failed_files)
        message = f"Batch processing failed for {failed_count}/{total_files} files"
        context = {
            "failed_count": failed_count,
            "total_files": total_files,
            "success_rate": f"{((total_files - failed_count) / total_files * 100):.1f}%"
        }
        super().__init__(message, exit_code=6, details=details, context=context)
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
    # Log the error
    cli_logger.error(f"CLI Error: {error.message}")
    if error.context:
        cli_logger.debug(f"Error context: {error.get_context_info()}")
    
    # Create error message with rich formatting
    error_text = Text()
    error_text.append("Error: ", style="bold red")
    error_text.append(error.message, style="red")
    
    console.print(error_text)
    
    # Show details if available and verbose mode is enabled
    if verbose and error.details:
        console.print(f"Details: {error.details}", style="dim red")
    
    # Show context in verbose mode
    if verbose and error.context:
        context_info = error.get_context_info()
        if context_info:
            console.print(f"Context: {context_info}", style="dim cyan")
    
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


def handle_unexpected_error(error: Exception, verbose: bool = False, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Handle unexpected errors with proper formatting.
    
    Args:
        error: The unexpected error
        verbose: Whether to show detailed error information
        context: Additional context information
    """
    # Log the unexpected error
    cli_logger.error(f"Unexpected error: {str(error)}")
    if context:
        cli_logger.debug(f"Error context: {context}")
    
    error_text = Text()
    error_text.append("Unexpected Error: ", style="bold red")
    error_text.append(str(error), style="red")
    
    console.print(error_text)
    
    # Show context in verbose mode
    if verbose and context:
        context_parts = [f"{k}: {v}" for k, v in context.items()]
        console.print(f"Context: {' | '.join(context_parts)}", style="dim cyan")
    
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


def safe_operation(operation_name: str, filepath: str = None, context: Optional[Dict[str, Any]] = None):
    """
    Decorator to safely execute operations with proper error handling.
    
    Args:
        operation_name: Name of the operation being performed
        filepath: Optional filepath being processed
        context: Additional context information
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                cli_logger.debug(f"Starting operation: {operation_name}")
                result = func(*args, **kwargs)
                cli_logger.debug(f"Completed operation: {operation_name}")
                return result
            except CLIError:
                # Re-raise CLI errors as-is
                cli_logger.debug(f"CLI error in operation {operation_name}: {str(e)}")
                raise
            except Exception as e:
                # Convert unexpected errors to ProcessingError
                cli_logger.error(f"Unexpected error in operation {operation_name}: {str(e)}")
                error_context = context or {}
                if filepath:
                    error_context['filepath'] = filepath
                
                if filepath:
                    raise ProcessingError(filepath, operation_name, str(e))
                else:
                    raise CLIError(f"Failed to {operation_name}: {str(e)}", context=error_context)
        return wrapper
    return decorator

def configure_logging(verbose: bool = False, debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure CLI logging based on user preferences.
    
    Args:
        verbose: Enable verbose output
        debug: Enable debug level logging
        log_file: Optional log file path
    """
    if debug:
        cli_logger.set_level('DEBUG')
    elif verbose:
        cli_logger.set_level('INFO')
    else:
        cli_logger.set_level('WARNING')
    
    if log_file:
        cli_logger.enable_file_logging(log_file)

def get_error_context(operation: str = None, file_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Create standardized error context dictionary.
    
    Args:
        operation: Operation being performed
        file_path: File being processed
        **kwargs: Additional context items
        
    Returns:
        Context dictionary
    """
    context = {}
    
    if operation:
        context['operation'] = operation
    
    if file_path:
        context['file_path'] = file_path
        if Path(file_path).exists():
            stat = Path(file_path).stat()
            context['file_size'] = stat.st_size
            context['file_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    context.update(kwargs)
    return context