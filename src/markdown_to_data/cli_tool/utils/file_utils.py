"""
File handling utilities for markdown-to-data CLI tool.

This module provides utilities for file operations including validation,
reading, writing, and path handling across all CLI commands.
"""

import os
import json
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import glob
from rich.console import Console
from rich.progress import Progress, TaskID

from .error_utils import (
    InvalidFileError, ProcessingError,
    validate_markdown_file, validate_json_file
)

console = Console()


def get_absolute_path(filepath: str) -> str:
    """
    Get absolute path from relative or absolute path.
    
    Args:
        filepath: Input file path
        
    Returns:
        Absolute path string
    """
    return str(Path(filepath).resolve())


def ensure_directory_exists(dirpath: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        dirpath: Directory path to ensure exists
        
    Raises:
        ProcessingError: If directory cannot be created
    """
    try:
        Path(dirpath).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ProcessingError(dirpath, "create directory", str(e))


def read_markdown_file(filepath: str) -> str:
    """
    Read markdown file content safely.
    
    Args:
        filepath: Path to markdown file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileError: If file is not valid markdown
    """
    validate_markdown_file(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ProcessingError(filepath, "read", str(e))


def read_json_file(filepath: str) -> Dict[str, Any]:
    """
    Read JSON file content safely.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileError: If file is not valid JSON
    """
    validate_json_file(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ProcessingError(filepath, "read JSON", str(e))


def write_json_file(filepath: str, data: Union[Dict[str, Any], List[Any]], indent: Optional[int] = 2) -> None:
    """
    Write data to JSON file safely.
    
    Args:
        filepath: Output file path
        data: Data to write
        indent: JSON indentation (None for compact)
        
    Raises:
        ProcessingError: If writing fails
    """
    try:
        # Ensure output directory exists
        output_dir = Path(filepath).parent
        ensure_directory_exists(str(output_dir))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        raise ProcessingError(filepath, "write JSON", str(e))


def write_text_file(filepath: str, content: str) -> None:
    """
    Write text content to file safely.
    
    Args:
        filepath: Output file path
        content: Text content to write
        
    Raises:
        ProcessingError: If writing fails
    """
    try:
        # Ensure output directory exists
        output_dir = Path(filepath).parent
        ensure_directory_exists(str(output_dir))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise ProcessingError(filepath, "write", str(e))


def find_markdown_files(
    pattern: str, 
    recursive: bool = True,
    exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    """
    Find markdown files matching pattern.
    
    Args:
        pattern: File pattern to match (supports glob patterns)
        recursive: Whether to search recursively
        exclude_patterns: Patterns to exclude from results
        
    Returns:
        List of matching file paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Handle different pattern types
    if recursive and '*' not in pattern:
        # If no glob pattern and recursive, search for markdown files
        if os.path.isdir(pattern):
            pattern = os.path.join(pattern, '**', '*.md')
        else:
            pattern = os.path.join(pattern, '**', '*.md')
    
    # Find files using glob
    if recursive:
        files = glob.glob(pattern, recursive=True)
    else:
        files = glob.glob(pattern)
    
    # Filter out excluded patterns
    filtered_files = []
    for filepath in files:
        excluded = False
        for exclude_pattern in exclude_patterns:
            if fnmatch.fnmatch(filepath, exclude_pattern):
                excluded = True
                break
        
        if not excluded:
            # Additional check to ensure it's a markdown file
            valid_extensions = ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']
            if any(filepath.lower().endswith(ext) for ext in valid_extensions):
                filtered_files.append(filepath)
    
    return sorted(filtered_files)


def find_json_files(
    pattern: str, 
    recursive: bool = True,
    exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    """
    Find JSON files matching pattern.
    
    Args:
        pattern: File pattern to match (supports glob patterns)
        recursive: Whether to search recursively
        exclude_patterns: Patterns to exclude from results
        
    Returns:
        List of matching JSON file paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Handle different pattern types
    if recursive and '*' not in pattern:
        if os.path.isdir(pattern):
            pattern = os.path.join(pattern, '**', '*.json')
        else:
            pattern = os.path.join(pattern, '**', '*.json')
    
    # Find files using glob
    if recursive:
        files = glob.glob(pattern, recursive=True)
    else:
        files = glob.glob(pattern)
    
    # Filter out excluded patterns and ensure JSON extension
    filtered_files = []
    for filepath in files:
        excluded = False
        for exclude_pattern in exclude_patterns:
            if fnmatch.fnmatch(filepath, exclude_pattern):
                excluded = True
                break
        
        if not excluded and filepath.lower().endswith('.json'):
            filtered_files.append(filepath)
    
    return sorted(filtered_files)


def generate_output_path(
    input_path: str, 
    output_dir: Optional[str] = None,
    output_extension: str = '.json',
    suffix: str = ''
) -> str:
    """
    Generate output file path based on input path.
    
    Args:
        input_path: Input file path
        output_dir: Output directory (None to use input directory)
        output_extension: Output file extension
        suffix: Suffix to add to filename
        
    Returns:
        Generated output file path
    """
    input_path_obj = Path(input_path)
    
    # Create output filename
    base_name = input_path_obj.stem
    if suffix:
        output_filename = f"{base_name}{suffix}{output_extension}"
    else:
        output_filename = f"{base_name}{output_extension}"
    
    # Determine output directory
    if output_dir:
        return str(Path(output_dir) / output_filename)
    else:
        return str(input_path_obj.parent / output_filename)


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get file information including size, modification time, etc.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = Path(filepath).stat()
        return {
            'path': filepath,
            'size': stat.st_size,
            'size_human': format_file_size(stat.st_size),
            'modified': stat.st_mtime,
            'readable': os.access(filepath, os.R_OK),
            'writable': os.access(filepath, os.W_OK),
        }
    except Exception as e:
        return {
            'path': filepath,
            'error': str(e)
        }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def validate_output_path(output_path: str, overwrite: bool = False) -> None:
    """
    Validate output path and handle overwrite logic.
    
    Args:
        output_path: Proposed output path
        overwrite: Whether to allow overwriting existing files
        
    Raises:
        InvalidFileError: If output path is invalid
        ProcessingError: If file exists and overwrite is False
    """
    output_path_obj = Path(output_path)
    
    # Check if parent directory is writable
    parent_dir = output_path_obj.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ProcessingError(str(parent_dir), "create output directory", str(e))
    
    if not os.access(parent_dir, os.W_OK):
        raise InvalidFileError(output_path, "Output directory is not writable")
    
    # Check if file exists and handle overwrite
    if output_path_obj.exists() and not overwrite:
        raise ProcessingError(
            output_path, 
            "write", 
            "File already exists (use --overwrite to replace)"
        )


class FileProcessor:
    """
    Context manager for processing multiple files with progress tracking.
    """
    
    def __init__(self, files: List[str], description: str = "Processing files"):
        self.files = files
        self.description = description
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.current_file: Optional[str] = None
        self.processed_count = 0
        self.failed_files: List[Tuple[str, str]] = []
    
    def __enter__(self) -> 'FileProcessor':
        if len(self.files) > 1:
            self.progress = Progress()
            self.progress.__enter__()
            self.task_id = self.progress.add_task(
                self.description, 
                total=len(self.files)
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)
    
    def process_file(self, filepath: str):
        """
        Context manager for processing a single file.
        
        Args:
            filepath: Path to file being processed
        """
        return FileProcessorContext(self, filepath)
    
    def update_progress(self, filepath: str, success: bool, error_msg: Optional[str] = None):
        """
        Update progress for a processed file.
        
        Args:
            filepath: Path to processed file
            success: Whether processing was successful
            error_msg: Error message if processing failed
        """
        self.processed_count += 1
        
        if not success and error_msg:
            self.failed_files.append((filepath, error_msg))
        
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=1)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get processing summary.
        
        Returns:
            Summary dictionary with statistics
        """
        return {
            'total_files': len(self.files),
            'processed': self.processed_count,
            'successful': self.processed_count - len(self.failed_files),
            'failed': len(self.failed_files),
            'failed_files': self.failed_files
        }


class FileProcessorContext:
    """Context manager for individual file processing within FileProcessor."""
    
    def __init__(self, processor: FileProcessor, filepath: str):
        self.processor = processor
        self.filepath = filepath
        self.success = False
        self.error_msg = None
    
    def __enter__(self) -> str:
        self.processor.current_file = self.filepath
        return self.filepath
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.success = True
        else:
            self.error_msg = str(exc_val) if exc_val else "Unknown error"
        
        self.processor.update_progress(
            self.filepath, 
            self.success, 
            self.error_msg or ""
        )
        
        # Don't suppress exceptions
        return False