"""
MD command implementations for markdown-to-data CLI tool.

This module provides the 'md' and 'batch-md' commands for converting
JSON data back to markdown format with filtering and formatting options.
"""

import click
from typing import Optional, List, Dict, Any, cast, Union
from datetime import datetime
from contextlib import nullcontext
from pathlib import Path

from markdown_to_data import Markdown, to_md_parser
from markdown_to_data.to_md.md_elements_list import MDElements
from ..utils.constants import SUPPORTED_ELEMENT_TYPES
from ..utils.error_utils import CLIError, validate_markdown_file, validate_json_file
from ..utils.file_utils import read_markdown_file, read_json_file, write_text_file, generate_output_path, validate_output_path
from ..utils.format_utils import console


def detect_file_type(filepath: str) -> str:
    """
    Detect file type based on extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File type ('markdown' or 'json')
        
    Raises:
        CLIError: If file type is not supported
    """
    filepath_lower = filepath.lower()
    
    if filepath_lower.endswith(('.md', '.markdown', '.mdown', '.mkd', '.mkdn')):
        return 'markdown'
    elif filepath_lower.endswith('.json'):
        return 'json'
    else:
        raise CLIError(
            f"Unsupported file type for '{filepath}'. "
            "Supported extensions: .md, .markdown, .mdown, .mkd, .mkdn, .json"
        )


def parse_element_filters(include: tuple, exclude: tuple) -> tuple[List[Union[MDElements, int]], List[Union[MDElements, int]]]:
    """
    Parse and validate include/exclude element filters.
    
    Args:
        include: Tuple of element types to include
        exclude: Tuple of element types to exclude
        
    Returns:
        Tuple of (include_list, exclude_list)
        
    Raises:
        CLIError: If invalid element types are provided
    """
    def parse_element_list(elements_tuple):
        if not elements_tuple:
            return []
        
        parsed_elements = []
        for element_group in elements_tuple:
            for element in element_group.split():
                element = element.strip().lower()
                if element:
                    parsed_elements.append(element)
        return parsed_elements
    
    include_list = parse_element_list(include)
    exclude_list = parse_element_list(exclude)
    
    # Special handling for 'all'
    if 'all' in include_list:
        include_list = ['all']
    
    # Validate element types
    all_elements = set(include_list + exclude_list)
    if 'all' in all_elements:
        all_elements.remove('all')  # 'all' is a special keyword
    
    # Expand 'headers' to individual header types for validation
    expanded_elements = set()
    for element in all_elements:
        if element == 'headers':
            expanded_elements.update(['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        else:
            expanded_elements.add(element)
    
    invalid_elements = expanded_elements - set(SUPPORTED_ELEMENT_TYPES)
    if invalid_elements:
        supported_types_str = ', '.join(sorted(SUPPORTED_ELEMENT_TYPES + ['all', 'headers']))
        raise CLIError(
            f"Invalid element type(s): {', '.join(invalid_elements)}. "
            f"Supported types: {supported_types_str}"
        )
    
    # Cast to MDElements type for type safety
    return [cast(Union[MDElements, int], item) for item in include_list], [cast(Union[MDElements, int], item) for item in exclude_list]


def validate_json_structure(data: Any, filepath: str) -> List[Dict[str, Any]]:
    """
    Validate that JSON data has the correct structure for markdown conversion.
    
    Args:
        data: JSON data to validate
        filepath: File path for error messages
        
    Returns:
        Validated data as list of dictionaries
        
    Raises:
        CLIError: If structure is invalid
    """
    if not isinstance(data, list):
        raise CLIError(
            f"Invalid JSON structure in '{filepath}': "
            "Expected a list of dictionaries (md_list format)"
        )
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise CLIError(
                f"Invalid JSON structure in '{filepath}': "
                f"Item at index {i} is not a dictionary. "
                "Expected md_list format with each item as a dictionary containing one markdown element"
            )
        
        if len(item) != 1:
            # Allow items with no keys (empty) or exactly one key
            if len(item) == 0:
                continue
            raise CLIError(
                f"Invalid JSON structure in '{filepath}': "
                f"Item at index {i} has {len(item)} keys, expected exactly 1. "
                "Each dictionary should contain exactly one markdown element type as key"
            )
        
        element_type = next(iter(item))
        if element_type not in SUPPORTED_ELEMENT_TYPES and element_type != 'header':
            # Note: We're a bit more lenient here to allow for future element types
            # but we warn about unknown types
            if not any(element_type.startswith(prefix) for prefix in ['h', 'def_', 'block']):
                console.print(
                    f"⚠️  Warning: Unknown element type '{element_type}' at index {i} in '{filepath}'",
                    style="yellow"
                )
    
    return data


def process_markdown_file(
    filepath: str,
    include_list: List[Union[MDElements, int]],
    exclude_list: List[Union[MDElements, int]],
    spacer: int
) -> str:
    """
    Process markdown file and return filtered markdown content.
    
    Args:
        filepath: Path to markdown file
        include_list: List of element types to include
        exclude_list: List of element types to exclude
        spacer: Number of empty lines between elements
        
    Returns:
        Processed markdown content
    """
    content = read_markdown_file(filepath)
    md = Markdown(content)
    
    # Use the to_md method with filtering options
    return md.to_md(include=include_list, exclude=exclude_list, spacer=spacer)


def process_json_file(
    filepath: str,
    include_list: List[Union[MDElements, int]],
    exclude_list: List[Union[MDElements, int]],
    spacer: int
) -> str:
    """
    Process JSON file and return markdown content.
    
    Args:
        filepath: Path to JSON file
        include_list: List of element types to include
        exclude_list: List of element types to exclude
        spacer: Number of empty lines between elements
        
    Returns:
        Generated markdown content
    """
    data = read_json_file(filepath)
    validated_data = validate_json_structure(data, filepath)
    
    # Use the to_md_parser function directly
    return to_md_parser(data=validated_data, include=include_list, exclude=exclude_list, spacer=spacer)


@click.command('md')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output markdown file path')
@click.option('--include', multiple=True, 
              help=f'Element types to include. Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES + ["all", "headers"]))}')
@click.option('--exclude', multiple=True, 
              help=f'Element types to exclude (overrides include). Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES + ["all", "headers"]))}')
@click.option('--spacer', type=int, default=1, 
              help='Number of empty lines between elements (default: 1, min: 0)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def md(ctx: click.Context, input_file: str, output: Optional[str], include: tuple, exclude: tuple,
       spacer: int, overwrite: bool, verbose: bool) -> None:
    """Convert JSON data or filter markdown back to markdown format.
    
    This command can process two types of input files:
    
    1. Markdown files (.md): Parses the markdown, applies filtering, and outputs
       filtered markdown content. Uses the to_md method internally.
    
    2. JSON files (.json): Converts JSON data (in md_list format) back to markdown.
       Uses the to_md_parser function internally.
    
    The JSON structure must be a list of dictionaries where each dictionary
    represents a markdown element (the md_list format from markdown-to-data).
    
    Filtering options:
    - --include: Only specified elements will be included
    - --exclude: Specified elements will be excluded (overrides include)
    - Use "headers" to include/exclude all header levels
    - Use "all" to include all elements (default behavior)
    
    Examples:
        m2d md document.md --exclude "metadata separator"
        m2d md data.json --include "h1 h2 table" --spacer 2
        m2d md document.md --exclude "headers" --output content.md
        m2d md data.json --include "all" --exclude "metadata"
    """
    try:
        if verbose:
            console.print(f"📖 Processing file: {input_file}", style="dim")
        
        # Detect and validate file type
        file_type = detect_file_type(input_file)
        
        if file_type == 'markdown':
            validate_markdown_file(input_file)
        else:  # json
            validate_json_file(input_file)
        
        if verbose:
            console.print(f"📋 Detected file type: {file_type}", style="dim")
        
        # Parse and validate filtering options
        include_list, exclude_list = parse_element_filters(include, exclude)
        
        # Validate spacer value
        if spacer < 0:
            raise CLIError(f"Invalid spacer value '{spacer}': must be 0 or greater")
        
        if verbose:
            if include_list:
                include_str = ', '.join(str(item) for item in include_list)
                console.print(f"📥 Include elements: {include_str}", style="dim")
            if exclude_list:
                exclude_str = ', '.join(str(item) for item in exclude_list)
                console.print(f"📤 Exclude elements: {exclude_str}", style="dim")
            console.print(f"📏 Spacer: {spacer} line(s)", style="dim")
        
        # Generate output path if not specified
        if not output:
            if file_type == 'json':
                # For JSON input, change extension to .md
                output = generate_output_path(input_file, output_extension='.md', suffix='')
            else:
                # For markdown input, add prefix to avoid overwriting
                output = generate_output_path(input_file, output_extension='.md', suffix='_new')
        
        # Validate output path
        validate_output_path(output, overwrite)
        
        # Process file based on type
        if file_type == 'markdown':
            markdown_content = process_markdown_file(input_file, include_list, exclude_list, spacer)
        else:  # json
            markdown_content = process_json_file(input_file, include_list, exclude_list, spacer)
        
        # Check if content is empty
        if not markdown_content.strip():
            if not ctx.obj.get('quiet', False):
                console.print("⚠️  Warning: Output is empty. No elements matched the filtering criteria.", style="yellow")
        
        # Write markdown output
        write_text_file(output, markdown_content)
        
        # Success message
        if not ctx.obj.get('quiet', False):
            console.print(f"✅ Converted: {input_file} → {output}", style="green")
            
            if verbose:
                line_count = len(markdown_content.splitlines())
                char_count = len(markdown_content)
                console.print(f"📊 Output: {line_count} lines, {char_count} characters", style="dim")
        
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Failed to convert file '{input_file}': {str(e)}")


@click.command('batch-md')
@click.argument('pattern', default='**/*.json')
@click.option('--output-dir', type=click.Path(), help='Output directory for markdown files')
@click.option('--include', multiple=True, 
              help=f'Element types to include. Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES + ["all", "headers"]))}')
@click.option('--exclude', multiple=True, 
              help=f'Element types to exclude (overrides include). Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES + ["all", "headers"]))}')
@click.option('--spacer', type=int, default=1, help='Number of empty lines between elements')
@click.option('--prefix', default='', help='Prefix for output filenames')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively')
@click.option('--parallel', '-p', is_flag=True, help='Process files in parallel')
@click.option('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
@click.option('--preserve-structure', is_flag=True, help='Preserve directory structure in output')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--continue-on-error', is_flag=True, help='Continue processing if individual files fail')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_md(ctx: click.Context, pattern: str, output_dir: Optional[str], include: tuple, exclude: tuple,
             spacer: int, prefix: str, recursive: bool, parallel: bool, max_workers: int,
             preserve_structure: bool, overwrite: bool, continue_on_error: bool, verbose: bool) -> None:
    """
    Convert multiple JSON files back to markdown format.
    
    This command processes multiple files in batch, converting JSON data
    (in md_list format) back to markdown format with optional filtering.
    
    By default, searches for JSON files, but can also process markdown files
    if the pattern specifies them.
    
    Examples:
    
        # Convert all JSON files in current directory
        m2d batch-md --output-dir converted/
        
        # Convert specific pattern with filtering
        m2d batch-md "*.json" --include "headers table" --prefix "filtered_"
        
        # Convert with parallel processing and preserve structure
        m2d batch-md "data/**/*.json" --parallel --preserve-structure --output-dir results
        
        # Convert markdown files with filtering
        m2d batch-md "docs/**/*.md" --exclude "metadata separator" --spacer 2
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
        
        # Parse element filters
        include_filters = parse_element_filters(include) if include else ['all']
        exclude_filters = parse_element_filters(exclude) if exclude else None
        
        # Find files to process (default to JSON files, but support markdown too)
        if pattern == '**/*.md':
            # If default pattern but user wants JSON files
            files = find_files_for_batch('**/*.json', recursive=recursive)
            if not files and recursive:
                # Fallback to markdown files if no JSON found
                files = find_files_for_batch(pattern, recursive=recursive)
        else:
            files = find_files_for_batch(pattern, recursive=recursive)
        
        if not files:
            console.print(f"❌ No files found matching pattern: {pattern}", style="red")
            return
            
        if verbose:
            console.print(f"📁 Found {len(files)} files to convert", style="blue")
            if include_filters != ['all']:
                console.print(f"📋 Including: {', '.join(include_filters)}", style="blue")
            if exclude_filters:
                console.print(f"❌ Excluding: {', '.join(exclude_filters)}", style="blue")
            
        # Create output directory if specified
        if output_dir:
            create_batch_output_directory(output_dir, overwrite=overwrite)
        else:
            output_dir = "."
            
        # Define processing function for batch processor
        def process_single_file(file_path: str) -> Dict[str, Any]:
            """Process a single file and return conversion result."""
            try:
                # Detect file type and process accordingly
                file_type = detect_file_type(file_path)
                
                if file_type == 'markdown':
                    # Process markdown file
                    markdown_content = process_markdown_file(
                        file_path, include_filters, exclude_filters, spacer
                    )
                elif file_type == 'json':
                    # Process JSON file
                    markdown_content = process_json_file(
                        file_path, include_filters, exclude_filters, spacer
                    )
                else:
                    raise CLIError(f"Unsupported file type for: {file_path}")
                
                # Determine output filename
                input_path = Path(file_path)
                
                if preserve_structure:
                    # Preserve relative directory structure
                    relative_path = input_path.relative_to(Path.cwd())
                    if file_type == 'json':
                        output_file = Path(output_dir) / relative_path.with_suffix('.md')
                    else:
                        # For markdown files, add prefix or suffix to avoid overwriting
                        stem = relative_path.stem
                        suffix = relative_path.suffix
                        new_name = f"{prefix}{stem}.converted{suffix}" if prefix else f"{stem}.converted{suffix}"
                        output_file = Path(output_dir) / relative_path.with_name(new_name)
                    # Ensure parent directories exist
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flatten to output directory
                    if file_type == 'json':
                        output_file = Path(output_dir) / f"{prefix}{input_path.stem}.md"
                    else:
                        output_file = Path(output_dir) / f"{prefix}{input_path.stem}.converted.md"
                
                # Write markdown file
                write_text_file(str(output_file), markdown_content)
                
                # Count elements in the output
                element_count = len([line for line in markdown_content.split('\n') if line.strip()])
                
                return {
                    'input_file': file_path,
                    'output_file': str(output_file),
                    'file_type': file_type,
                    'element_count': element_count,
                    'file_size': output_file.stat().st_size if output_file.exists() else 0,
                    'include_filters': include_filters,
                    'exclude_filters': exclude_filters or []
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
        with console.status("[bold blue]Converting to markdown...") if ctx.obj.get('quiet', False) else nullcontext():
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
            
            console.print(f"📊 Generated {total_elements} total lines of markdown", style="dim")
            console.print(f"💾 Created {format_file_size(total_size)} of markdown files", style="dim")
            
        # Print summary
        if not ctx.obj.get('quiet', False):
            print_batch_summary(result, "Markdown conversion")
            
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
                error_log_file = Path(output_dir) / "markdown_conversion_errors.txt"
                error_collector.save_error_log(str(error_log_file))
                if verbose:
                    console.print(f"📝 Error log saved to: {error_log_file}", style="yellow")
                    
        if verbose:
            console.print(f"✅ Batch markdown conversion completed: {len(result.successes)} successful, {len(result.errors)} failed", style="green")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Batch markdown conversion failed: {str(e)}")


def write_text_file(file_path: str, content: str) -> None:
    """Write text content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise CLIError(f"Failed to write text file '{file_path}': {str(e)}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"