"""
File handling utilities for markdown-to-data CLI tool.

This module provides utilities for file operations including validation,
reading, writing, and path handling across all CLI commands.
"""

import os
import json
import fnmatch
import psutil
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Iterator, Generator
import glob
from rich.console import Console
from rich.progress import Progress, TaskID

from .error_utils import (
    InvalidFileError, ProcessingError,
    validate_markdown_file, validate_json_file, cli_logger
)
from .constants import FILE_SIZE_LIMITS

console = Console()


class MemoryMonitor:
    """Monitor memory usage during file processing operations."""
    
    def __init__(self, warning_threshold_mb: int = 512):
        self.warning_threshold_mb = warning_threshold_mb
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }
    
    def check_memory_usage(self) -> bool:
        """
        Check if memory usage exceeds warning threshold.
        
        Returns:
            True if memory usage is acceptable, False if threshold exceeded
        """
        current_memory = self.get_memory_usage()
        
        if current_memory['rss_mb'] > self.warning_threshold_mb:
            cli_logger.warning(
                f"High memory usage detected: {current_memory['rss_mb']:.1f}MB "
                f"(threshold: {self.warning_threshold_mb}MB)"
            )
            return False
        
        return True
    
    def force_garbage_collection(self) -> Dict[str, float]:
        """Force garbage collection and return memory statistics."""
        before_memory = self.get_memory_usage()
        gc.collect()
        after_memory = self.get_memory_usage()
        
        freed_mb = before_memory['rss_mb'] - after_memory['rss_mb']
        cli_logger.debug(f"Garbage collection freed {freed_mb:.1f}MB")
        
        return after_memory


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


def read_markdown_file(filepath: str, stream_large_files: bool = True) -> str:
    """
    Read markdown file content safely with optional streaming for large files.
    
    Args:
        filepath: Path to markdown file
        stream_large_files: Whether to use streaming for large files
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileError: If file is not valid markdown
    """
    validate_markdown_file(filepath)
    
    # Check file size
    file_size = Path(filepath).stat().st_size
    
    # Warn about large files
    if file_size > FILE_SIZE_LIMITS['warning_threshold']:
        size_mb = file_size / (1024 * 1024)
        cli_logger.warning(f"Reading large file ({size_mb:.1f}MB): {filepath}")
    
    # Refuse extremely large files
    if file_size > FILE_SIZE_LIMITS['max_file_size']:
        size_mb = file_size / (1024 * 1024)
        raise InvalidFileError(
            filepath, 
            f"File too large ({size_mb:.1f}MB). Maximum allowed: {FILE_SIZE_LIMITS['max_file_size'] / (1024 * 1024):.1f}MB"
        )
    
    try:
        if stream_large_files and file_size > FILE_SIZE_LIMITS['warning_threshold']:
            # Stream large files in chunks
            content_chunks = []
            with open(filepath, 'r', encoding='utf-8') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    content_chunks.append(chunk)
            return ''.join(content_chunks)
        else:
            # Read normally for smaller files
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        raise ProcessingError(filepath, "read", str(e))


def read_json_file(filepath: str, stream_large_files: bool = True) -> Dict[str, Any]:
    """
    Read JSON file content safely with memory monitoring.
    
    Args:
        filepath: Path to JSON file
        stream_large_files: Whether to use streaming for large files
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileError: If file is not valid JSON
    """
    validate_json_file(filepath)
    
    # Check file size
    file_size = Path(filepath).stat().st_size
    
    # Warn about large files
    if file_size > FILE_SIZE_LIMITS['warning_threshold']:
        size_mb = file_size / (1024 * 1024)
        cli_logger.warning(f"Reading large JSON file ({size_mb:.1f}MB): {filepath}")
    
    # Refuse extremely large files
    if file_size > FILE_SIZE_LIMITS['max_file_size']:
        size_mb = file_size / (1024 * 1024)
        raise InvalidFileError(
            filepath, 
            f"JSON file too large ({size_mb:.1f}MB). Maximum allowed: {FILE_SIZE_LIMITS['max_file_size'] / (1024 * 1024):.1f}MB"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ProcessingError(filepath, "read JSON", str(e))


def write_json_file(filepath: str, data: Union[Dict[str, Any], List[Any]], indent: Optional[int] = 2, 
                   monitor_memory: bool = True) -> None:
    """
    Write data to JSON file safely with memory monitoring.
    
    Args:
        filepath: Output file path
        data: Data to write
        indent: JSON indentation (None for compact)
        monitor_memory: Whether to monitor memory usage during write
        
    Raises:
        ProcessingError: If writing fails
    """
    memory_monitor = MemoryMonitor() if monitor_memory else None
    
    try:
        # Ensure output directory exists
        output_dir = Path(filepath).parent
        ensure_directory_exists(str(output_dir))
        
        if memory_monitor:
            memory_monitor.check_memory_usage()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        if memory_monitor:
            final_memory = memory_monitor.get_memory_usage()
            cli_logger.debug(f"JSON write completed. Memory usage: {final_memory['rss_mb']:.1f}MB")
            
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
    Get comprehensive file information including size, modification time, etc.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = Path(filepath).stat()
        file_size = stat.st_size
        
        # Determine file category based on size
        if file_size > FILE_SIZE_LIMITS['max_file_size']:
            size_category = 'too_large'
        elif file_size > FILE_SIZE_LIMITS['warning_threshold']:
            size_category = 'large'
        elif file_size > 10240:  # 10KB
            size_category = 'medium'
        else:
            size_category = 'small'
        
        return {
            'path': filepath,
            'size': file_size,
            'size_human': format_file_size(file_size),
            'size_category': size_category,
            'modified': stat.st_mtime,
            'readable': os.access(filepath, os.R_OK),
            'writable': os.access(filepath, os.W_OK),
            'is_large': file_size > FILE_SIZE_LIMITS['warning_threshold'],
            'is_too_large': file_size > FILE_SIZE_LIMITS['max_file_size']
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
    Context manager for processing multiple files with progress tracking and memory monitoring.
    """
    
    def __init__(self, files: List[str], description: str = "Processing files", 
                 monitor_memory: bool = True):
        self.files = files
        self.description = description
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.current_file: Optional[str] = None
        self.processed_count = 0
        self.failed_files: List[Tuple[str, str]] = []
        self.memory_monitor = MemoryMonitor() if monitor_memory else None
        self.start_memory: Optional[Dict[str, float]] = None
    
    def __enter__(self) -> 'FileProcessor':
        if self.memory_monitor:
            self.start_memory = self.memory_monitor.get_memory_usage()
            cli_logger.debug(f"Starting file processing. Initial memory: {self.start_memory['rss_mb']:.1f}MB")
        
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
        Update progress for a processed file with memory monitoring.
        
        Args:
            filepath: Path to processed file
            success: Whether processing was successful
            error_msg: Error message if processing failed
        """
        self.processed_count += 1
        
        if not success and error_msg:
            self.failed_files.append((filepath, error_msg))
        
        # Monitor memory usage
        if self.memory_monitor:
            if not self.memory_monitor.check_memory_usage():
                # Force garbage collection if memory usage is high
                self.memory_monitor.force_garbage_collection()
        
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=1)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get processing summary with memory statistics.
        
        Returns:
            Summary dictionary with statistics
        """
        summary = {
            'total_files': len(self.files),
            'processed': self.processed_count,
            'successful': self.processed_count - len(self.failed_files),
            'failed': len(self.failed_files),
            'failed_files': self.failed_files
        }
        
        # Add memory statistics if monitoring is enabled
        if self.memory_monitor and self.start_memory:
            current_memory = self.memory_monitor.get_memory_usage()
            summary['memory'] = {
                'start_mb': self.start_memory['rss_mb'],
                'end_mb': current_memory['rss_mb'],
                'peak_mb': max(self.start_memory['rss_mb'], current_memory['rss_mb']),
                'change_mb': current_memory['rss_mb'] - self.start_memory['rss_mb']
            }
        
        return summary


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