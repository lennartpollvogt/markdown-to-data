"""
Convert command implementations for markdown-to-data CLI tool.

This module provides the 'convert' and 'batch-convert' commands for converting
markdown files to JSON format.
"""

import click
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from contextlib import nullcontext

from markdown_to_data import Markdown
from ..utils.constants import COMMAND_DESCRIPTIONS, OutputFormat
from ..utils.error_utils import CLIError, validate_markdown_file, handle_cli_error
from ..utils.file_utils import read_markdown_file, write_json_file, generate_output_path, validate_output_path
from ..utils.format_utils import console, print_json_output


@click.command('convert')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--structure', '-s', default='dict', 
              type=click.Choice(['list', 'dict']), help='Output structure format')
@click.option('--indent', type=int, default=2, help='JSON indentation level')
@click.option('--compact', is_flag=True, help='Use compact JSON format')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def convert(ctx: click.Context, input_file: str, output: Optional[str], structure: str, 
           indent: int, compact: bool, overwrite: bool, verbose: bool) -> None:
    """Convert a markdown file to JSON format.
    
    This command converts a markdown file into structured JSON data that can be
    easily processed programmatically. Supports two output structures:
    
    - list: Each markdown element as a separate dictionary in a list
    - dict: Nested structure using headers as keys (default)
    
    Examples:
        m2d convert document.md
        m2d convert document.md --structure list
        m2d convert document.md --output data.json --compact
    """
    try:
        if verbose:
            console.print(f"📖 Converting file: {input_file}", style="dim")
        
        # Validate input file
        validate_markdown_file(input_file)
        
        # Generate output path if not specified
        if not output:
            output = generate_output_path(input_file, output_extension='.json')
        
        # Validate output path
        validate_output_path(output, overwrite)
        
        # Read and parse markdown
        content = read_markdown_file(input_file)
        md = Markdown(content)
        
        # Get data in requested format
        if structure == 'list':
            data = md.md_list
        else:  # dict
            data = md.md_dict
        
        # Set indentation based on compact flag
        json_indent = None if compact else indent
        
        # Write JSON output
        write_json_file(output, data, json_indent)
        
        # Success message
        if not ctx.obj.get('quiet', False):
            console.print(f"✅ Converted: {input_file} → {output}", style="green")
            
            if verbose:
                element_count = len(md.md_list)
                console.print(f"📊 Processed {element_count} markdown elements", style="dim")
        
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Failed to convert file '{input_file}': {str(e)}")


@click.command('batch-convert')
@click.argument('pattern', default='**/*.md')
@click.option('--output-dir', type=click.Path(), help='Output directory for JSON files')
@click.option('--format', '-f', default='list', help='Output format (list, dict)')
@click.option('--indent', type=int, default=2, help='JSON indentation level')
@click.option('--compact', is_flag=True, help='Use compact JSON format')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively')
@click.option('--parallel', '-p', is_flag=True, help='Process files in parallel')
@click.option('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
@click.option('--preserve-structure', is_flag=True, help='Preserve directory structure in output')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--continue-on-error', is_flag=True, help='Continue processing if individual files fail')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_convert(ctx: click.Context, pattern: str, output_dir: Optional[str], format: str,
                 indent: int, compact: bool, recursive: bool, parallel: bool, max_workers: int,
                 preserve_structure: bool, overwrite: bool, continue_on_error: bool, verbose: bool) -> None:
    """
    Convert multiple markdown files to JSON format.
    
    PATTERN specifies the file pattern to search for (default: **/*.md).
    Supports glob patterns like '*.md', 'docs/**/*.md', etc.
    
    Examples:
    
        # Convert all markdown files in current directory and subdirectories
        m2d batch-convert
        
        # Convert specific pattern with output directory
        m2d batch-convert "docs/**/*.md" --output-dir json_output
        
        # Convert with parallel processing and preserve directory structure
        m2d batch-convert --parallel --preserve-structure --output-dir results
        
        # Convert to dictionary format with custom indentation
        m2d batch-convert --format dict --indent 4 --output-dir results
    """
    from ..utils.batch_utils import (
        BatchProcessor, find_files_for_batch, create_batch_output_directory,
        save_batch_results, print_batch_summary, validate_batch_options,
        BatchErrorCollector
    )
    
    console = Console()
    
    try:
        # Validate options
        validate_batch_options(
            pattern=pattern,
            output_dir=output_dir,
            max_workers=max_workers,
            overwrite=overwrite
        )
        
        # Validate format
        if format not in ['list', 'dict']:
            raise CLIError(f"Invalid format '{format}'. Must be 'list' or 'dict'")
            
        # Find files to process
        files = find_files_for_batch(pattern, recursive=recursive)
        
        if not files:
            console.print(f"❌ No files found matching pattern: {pattern}", style="red")
            return
            
        if verbose:
            console.print(f"📁 Found {len(files)} files to convert", style="blue")
            
        # Create output directory if specified
        if output_dir:
            create_batch_output_directory(output_dir, overwrite=overwrite)
        else:
            output_dir = "."
            
        # Define processing function for batch processor
        def process_single_file(file_path: str) -> Dict[str, Any]:
            """Process a single file and return conversion result."""
            try:
                # Convert markdown to data
                md = Markdown(file_path)
                
                # Get data in requested format
                if format == 'list':
                    data = md.md_list
                else:  # format == 'dict'
                    data = md.md_dict
                    
                # Determine output filename
                input_path = Path(file_path)
                
                if preserve_structure:
                    # Preserve relative directory structure
                    relative_path = input_path.relative_to(Path.cwd())
                    output_file = Path(output_dir) / relative_path.with_suffix('.json')
                    # Ensure parent directories exist
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flatten to output directory
                    output_file = Path(output_dir) / f"{input_path.stem}.json"
                
                # Write JSON file
                write_json_file(
                    str(output_file),
                    data,
                    indent=None if compact else indent
                )
                
                # Return result info
                element_count = len(data) if isinstance(data, list) else count_dict_elements(data)
                
                return {
                    'input_file': file_path,
                    'output_file': str(output_file),
                    'format': format,
                    'element_count': element_count,
                    'file_size': output_file.stat().st_size if output_file.exists() else 0
                }
                
            except Exception as e:
                if not continue_on_error:
                    raise
                # Return error info for failed files
                return {
                    'input_file': file_path,
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Set up batch processor
        processor = BatchProcessor(
            task_name="markdown conversion",
            max_workers=max_workers if parallel else 1,
            show_progress=not ctx.obj.get('quiet', False)
        )
        
        # Process files
        with console.status("[bold blue]Converting files...") if ctx.obj.get('quiet', False) else nullcontext():
            result = processor.process_files(files, process_single_file)
            
        # Handle successful conversions
        if result.successes and verbose:
            total_elements = sum(
                success['result'].get('element_count', 0) 
                for success in result.successes 
                if 'element_count' in success['result']
            )
            total_size = sum(
                success['result'].get('file_size', 0)
                for success in result.successes
                if 'file_size' in success['result']
            )
            
            console.print(f"📊 Converted {total_elements} total elements", style="dim")
            console.print(f"💾 Generated {format_file_size(total_size)} of JSON data", style="dim")
            
        # Print summary
        if not ctx.obj.get('quiet', False):
            print_batch_summary(result, "Conversion")
            
        # Handle errors
        if result.errors:
            error_collector = BatchErrorCollector()
            for error in result.errors:
                error_collector.add_error(error['file'], error['error'])
                
            if not continue_on_error:
                console.print(f"\n❌ {len(result.errors)} files failed to convert", style="red")
                error_collector.print_error_summary()
                
            # Save error log if output directory specified
            if output_dir:
                error_log_file = Path(output_dir) / "conversion_errors.txt"
                error_collector.save_error_log(str(error_log_file))
                if verbose:
                    console.print(f"📝 Error log saved to: {error_log_file}", style="yellow")
                    
        if verbose:
            console.print(f"✅ Batch conversion completed: {len(result.successes)} successful, {len(result.errors)} failed", style="green")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Batch conversion failed: {str(e)}")


def count_dict_elements(data: Dict[str, Any]) -> int:
    """Count the number of elements in a nested dictionary structure."""
    count = 0
    for value in data.values():
        if isinstance(value, dict):
            if any(key in value for key in ['header', 'paragraph', 'list', 'table', 'code', 'blockquote', 'metadata', 'def_list', 'separator']):
                count += 1
            else:
                count += count_dict_elements(value)
        elif isinstance(value, list):
            count += len(value)
    return count


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"