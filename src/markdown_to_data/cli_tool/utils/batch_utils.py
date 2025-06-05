"""
Batch processing utilities for markdown-to-data CLI tool.

This module provides utilities for processing multiple files efficiently,
including parallel processing, progress tracking, and error collection.
"""

import os
import json
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple, Iterator
from dataclasses import dataclass
from datetime import datetime
import threading
import time

from rich.console import Console
from rich.progress import Progress, TaskID, TimeElapsedColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .file_utils import find_markdown_files, find_json_files, FileProcessor
from .error_utils import BatchProcessingError, ProcessingError, CLIError
from .format_utils import create_summary_table, print_json_output
from .constants import BATCH_SETTINGS, cli_config

console = Console()


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_files: int
    processed_files: int
    successful_files: int
    failed_files: int
    processing_time: float
    errors: List[Tuple[str, str]]
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]


@dataclass
class FileTask:
    """Represents a file processing task."""
    filepath: str
    operation: str
    options: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class BatchProcessor:
    """
    High-level batch processor for markdown files.
    
    Handles parallel processing, progress tracking, and error collection
    for batch operations on multiple files.
    """
    
    def __init__(
        self,
        files: List[str],
        operation_name: str,
        max_workers: Optional[int] = None,
        show_progress: bool = True
    ):
        self.files = files
        self.operation_name = operation_name
        self.max_workers = max_workers or BATCH_SETTINGS['max_workers']
        self.show_progress = show_progress and not cli_config.quiet
        
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Tuple[str, str]] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Thread-safe counters
        self._lock = threading.Lock()
        self._processed_count = 0
        self._successful_count = 0
        self._failed_count = 0
    
    def process_files(
        self,
        processor_func: Callable[[str, Dict[str, Any]], Any],
        options: Dict[str, Any] = None
    ) -> BatchResult:
        """
        Process multiple files using the provided processor function.
        
        Args:
            processor_func: Function to process each file
            options: Options to pass to processor function
            
        Returns:
            BatchResult with processing statistics and results
        """
        if options is None:
            options = {}
        
        self.start_time = time.time()
        
        if len(self.files) == 1 or not self.show_progress:
            # Single-threaded processing for single file or when progress is disabled
            return self._process_sequentially(processor_func, options)
        else:
            # Multi-threaded processing for multiple files
            return self._process_in_parallel(processor_func, options)
    
    def _process_sequentially(
        self,
        processor_func: Callable[[str, Dict[str, Any]], Any],
        options: Dict[str, Any]
    ) -> BatchResult:
        """Process files sequentially."""
        for filepath in self.files:
            try:
                result = processor_func(filepath, options)
                self._add_success(filepath, result)
                
                if cli_config.verbose:
                    console.print(f"✅ Processed: {filepath}", style="green")
                    
            except Exception as e:
                self._add_error(filepath, str(e))
                
                if cli_config.verbose:
                    console.print(f"❌ Failed: {filepath} - {str(e)}", style="red")
        
        return self._create_result()
    
    def _process_in_parallel(
        self,
        processor_func: Callable[[str, Dict[str, Any]], Any],
        options: Dict[str, Any]
    ) -> BatchResult:
        """Process files in parallel with progress tracking."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            console=console,
            disable=not self.show_progress
        ) as progress:
            
            task = progress.add_task(
                f"Processing {self.operation_name}...",
                total=len(self.files)
            )
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(processor_func, filepath, options): filepath
                    for filepath in self.files
                }
                
                # Process completed tasks
                for future in concurrent.futures.as_completed(future_to_file):
                    filepath = future_to_file[future]
                    
                    try:
                        result = future.result()
                        self._add_success(filepath, result)
                        
                        if cli_config.verbose:
                            console.print(f"✅ Processed: {filepath}", style="green")
                            
                    except Exception as e:
                        self._add_error(filepath, str(e))
                        
                        if cli_config.verbose:
                            console.print(f"❌ Failed: {filepath} - {str(e)}", style="red")
                    
                    finally:
                        progress.advance(task)
        
        return self._create_result()
    
    def _add_success(self, filepath: str, result: Any) -> None:
        """Thread-safe method to add successful result."""
        with self._lock:
            self.results.append({
                'filepath': filepath,
                'result': result,
                'status': 'success'
            })
            self._processed_count += 1
            self._successful_count += 1
    
    def _add_error(self, filepath: str, error_msg: str) -> None:
        """Thread-safe method to add error result."""
        with self._lock:
            self.errors.append((filepath, error_msg))
            self._processed_count += 1
            self._failed_count += 1
    
    def _create_result(self) -> BatchResult:
        """Create final batch result."""
        self.end_time = time.time()
        processing_time = self.end_time - (self.start_time or 0)
        
        # Create summary statistics
        summary = {
            'operation': self.operation_name,
            'total_files': len(self.files),
            'processed_files': self._processed_count,
            'successful_files': self._successful_count,
            'failed_files': self._failed_count,
            'success_rate': (self._successful_count / len(self.files) * 100) if self.files else 0,
            'processing_time': processing_time,
            'avg_time_per_file': processing_time / len(self.files) if self.files else 0,
            'files_per_second': len(self.files) / processing_time if processing_time > 0 else 0
        }
        
        return BatchResult(
            total_files=len(self.files),
            processed_files=self._processed_count,
            successful_files=self._successful_count,
            failed_files=self._failed_count,
            processing_time=processing_time,
            errors=self.errors,
            results=self.results,
            summary=summary
        )


def find_files_for_batch(
    pattern: str,
    file_type: str = 'markdown',
    recursive: bool = True,
    exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    """
    Find files for batch processing based on pattern and type.
    
    Args:
        pattern: File pattern to match
        file_type: Type of files to find ('markdown' or 'json')
        recursive: Whether to search recursively
        exclude_patterns: Patterns to exclude
        
    Returns:
        List of matching file paths
        
    Raises:
        CLIError: If no files found or invalid pattern
    """
    if file_type == 'markdown':
        files = find_markdown_files(pattern, recursive, exclude_patterns)
    elif file_type == 'json':
        files = find_json_files(pattern, recursive, exclude_patterns)
    else:
        raise CLIError(f"Unsupported file type: {file_type}")
    
    if not files:
        raise CLIError(f"No {file_type} files found matching pattern: {pattern}")
    
    # Warn if processing many files
    if len(files) > BATCH_SETTINGS['max_files_warning'] and not cli_config.quiet:
        console.print(
            f"⚠️  Processing {len(files)} files. This may take a while...",
            style="yellow"
        )
    
    return files


def create_batch_output_directory(
    output_dir: Optional[str],
    operation_name: str,
    create_timestamped: bool = False
) -> str:
    """
    Create and validate batch output directory.
    
    Args:
        output_dir: Specified output directory (None for default)
        operation_name: Name of the operation for default directory
        create_timestamped: Whether to create timestamped subdirectory
        
    Returns:
        Path to output directory
        
    Raises:
        ProcessingError: If directory cannot be created
    """
    if output_dir is None:
        # Use current directory with operation-specific subdirectory
        output_dir = f"md2data_{operation_name}_output"
    
    if create_timestamped:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_dir, timestamp)
    
    # Create directory
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ProcessingError(output_dir, "create output directory", str(e))
    
    return output_dir


def save_batch_results(
    results: List[Dict[str, Any]],
    output_dir: str,
    format_type: str = 'json',
    filename: str = 'batch_results'
) -> str:
    """
    Save batch processing results to file.
    
    Args:
        results: List of processing results
        output_dir: Output directory
        format_type: Output format ('json', 'summary')
        filename: Base filename for output
        
    Returns:
        Path to saved file
        
    Raises:
        ProcessingError: If saving fails
    """
    if format_type == 'json':
        output_path = os.path.join(output_dir, f"{filename}.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ProcessingError(output_path, "save batch results", str(e))
    
    elif format_type == 'summary':
        output_path = os.path.join(output_dir, f"{filename}_summary.txt")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Batch Processing Summary\n")
                f.write("=" * 50 + "\n\n")
                
                total_files = len(results)
                successful = sum(1 for r in results if r.get('status') == 'success')
                failed = total_files - successful
                
                f.write(f"Total files processed: {total_files}\n")
                f.write(f"Successful: {successful}\n")
                f.write(f"Failed: {failed}\n")
                f.write(f"Success rate: {(successful/total_files*100):.1f}%\n\n")
                
                if failed > 0:
                    f.write("Failed files:\n")
                    f.write("-" * 20 + "\n")
                    for result in results:
                        if result.get('status') != 'success':
                            f.write(f"❌ {result.get('filepath', 'unknown')}\n")
                
        except Exception as e:
            raise ProcessingError(output_path, "save batch summary", str(e))
    
    else:
        raise CLIError(f"Unsupported save format: {format_type}")
    
    return output_path


def print_batch_summary(batch_result: BatchResult) -> None:
    """
    Print a formatted summary of batch processing results.
    
    Args:
        batch_result: Result of batch processing
    """
    if cli_config.quiet:
        return
    
    summary = batch_result.summary
    
    # Create and print summary table
    table = Table(title=f"Batch {summary['operation'].title()} Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")
    
    table.add_row("Total Files", str(summary['total_files']))
    table.add_row("Processed", str(summary['processed_files']))
    table.add_row("Successful", f"{summary['successful_files']} ({summary['success_rate']:.1f}%)")
    table.add_row("Failed", str(summary['failed_files']))
    table.add_row("Processing Time", f"{summary['processing_time']:.2f}s")
    table.add_row("Avg Time/File", f"{summary['avg_time_per_file']:.3f}s")
    table.add_row("Files/Second", f"{summary['files_per_second']:.1f}")
    
    console.print(table)
    
    # Show errors if any and verbose mode
    if batch_result.errors and cli_config.verbose:
        console.print("\n❌ Failed Files:", style="red bold")
        for filepath, error in batch_result.errors:
            console.print(f"  • {filepath}: {error}", style="red")
    
    # Final status message
    if batch_result.failed_files == 0:
        console.print(f"\n✅ All {batch_result.total_files} files processed successfully!", style="green bold")
    else:
        console.print(
            f"\n⚠️  {batch_result.successful_files}/{batch_result.total_files} files processed successfully",
            style="yellow bold"
        )


def validate_batch_options(
    pattern: str,
    output_dir: Optional[str] = None,
    max_files: int = 1000
) -> None:
    """
    Validate batch processing options.
    
    Args:
        pattern: File pattern to validate
        output_dir: Output directory to validate
        max_files: Maximum allowed number of files
        
    Raises:
        CLIError: If validation fails
    """
    # Validate pattern
    if not pattern or not pattern.strip():
        raise CLIError("File pattern cannot be empty")
    
    # Check if pattern might match too many files
    try:
        import glob
        potential_matches = glob.glob(pattern, recursive=True)
        if len(potential_matches) > max_files:
            raise CLIError(
                f"Pattern matches {len(potential_matches)} files, which exceeds limit of {max_files}. "
                "Please use a more specific pattern."
            )
    except Exception:
        # If glob fails, continue - the actual file finding will handle errors
        pass
    
    # Validate output directory if specified
    if output_dir:
        if os.path.exists(output_dir) and not os.path.isdir(output_dir):
            raise CLIError(f"Output path exists but is not a directory: {output_dir}")
        
        # Check if we can create the directory
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CLIError(f"Cannot create output directory '{output_dir}': {str(e)}")


def chunk_files(files: List[str], chunk_size: Optional[int] = None) -> Iterator[List[str]]:
    """
    Split files into chunks for processing.
    
    Args:
        files: List of files to chunk
        chunk_size: Size of each chunk (None for default)
        
    Yields:
        Lists of files in each chunk
    """
    if chunk_size is None:
        chunk_size = BATCH_SETTINGS['chunk_size']
    
    for i in range(0, len(files), chunk_size):
        yield files[i:i + chunk_size]


class BatchErrorCollector:
    """Utility class for collecting and reporting batch processing errors."""
    
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []  # (filepath, operation, error)
    
    def add_error(self, filepath: str, operation: str, error: str) -> None:
        """Add an error to the collection."""
        self.errors.append((filepath, operation, error))
    
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def get_error_count(self) -> int:
        """Get the total number of errors."""
        return len(self.errors)
    
    def get_failed_files(self) -> List[str]:
        """Get list of files that failed processing."""
        return [filepath for filepath, _, _ in self.errors]
    
    def print_error_summary(self) -> None:
        """Print a summary of all collected errors."""
        if not self.errors:
            return
        
        console.print(f"\n❌ {len(self.errors)} Error(s) Occurred:", style="red bold")
        
        for filepath, operation, error in self.errors:
            console.print(f"  • {operation} failed for {filepath}: {error}", style="red")
    
    def save_error_log(self, output_path: str) -> None:
        """Save error log to file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Batch Processing Error Log\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total errors: {len(self.errors)}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                for i, (filepath, operation, error) in enumerate(self.errors, 1):
                    f.write(f"{i}. File: {filepath}\n")
                    f.write(f"   Operation: {operation}\n")
                    f.write(f"   Error: {error}\n\n")
                    
        except Exception as e:
            console.print(f"Failed to save error log: {e}", style="red")