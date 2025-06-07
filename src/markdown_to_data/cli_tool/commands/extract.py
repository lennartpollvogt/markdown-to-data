"""
Extract command implementations for markdown-to-data CLI tool.

This module provides the 'extract' and 'batch-extract' commands for extracting
specific elements from markdown files.
"""

import click
from typing import Optional, List, Dict, Any, Set, Union
from datetime import datetime
from contextlib import nullcontext

from markdown_to_data import Markdown
from ..utils.constants import SUPPORTED_ELEMENT_TYPES
from ..utils.error_utils import CLIError, validate_markdown_file
from ..utils.file_utils import read_markdown_file, write_json_file, generate_output_path, validate_output_path
from ..utils.format_utils import console


def parse_element_types(elements: tuple) -> Set[str]:
    """
    Parse and validate element types from command line input.
    
    Args:
        elements: Tuple of element type strings
        
    Returns:
        Set of validated element types
        
    Raises:
        CLIError: If invalid element types are provided
    """
    if not elements:
        # Default: extract all supported element types
        return set(SUPPORTED_ELEMENT_TYPES)
    
    # Flatten space-separated element lists
    parsed_elements = set()
    for element_group in elements:
        for element in element_group.split():
            element = element.strip().lower()
            if element:
                parsed_elements.add(element)
    
    # Validate element types
    invalid_elements = []
    valid_elements = set()
    
    for element in parsed_elements:
        if element == 'headers':
            # Special case: 'headers' expands to all header types
            valid_elements.update(['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        elif element in SUPPORTED_ELEMENT_TYPES:
            valid_elements.add(element)
        else:
            invalid_elements.append(element)
    
    if invalid_elements:
        supported_types_str = ', '.join(sorted(SUPPORTED_ELEMENT_TYPES))
        raise CLIError(
            f"Invalid element type(s): {', '.join(invalid_elements)}. "
            f"Supported types: {supported_types_str}"
        )
    
    return valid_elements


def filter_elements_by_type(md_list: List[Dict[str, Any]], target_elements: Set[str]) -> List[Dict[str, Any]]:
    """
    Filter markdown elements by specified types.
    
    Args:
        md_list: List of markdown elements from Markdown.md_list
        target_elements: Set of element types to extract
        
    Returns:
        Filtered list of markdown elements
    """
    filtered_elements = []
    
    for element in md_list:
        if not element or not isinstance(element, dict):
            continue
            
        element_type = next(iter(element))
        
        # Handle header level filtering
        if element_type == 'header':
            header_level = element['header'].get('level', 1)
            header_type = f'h{header_level}'
            
            # Include if 'header' or specific level (h1, h2, etc.) is requested
            if 'header' in target_elements or header_type in target_elements:
                filtered_elements.append(element)
        else:
            # Include if element type is in target set
            if element_type in target_elements:
                filtered_elements.append(element)
    
    return filtered_elements


def group_elements_by_type(elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group extracted elements by their type.
    
    Args:
        elements: List of markdown elements
        
    Returns:
        Dictionary with element types as keys and lists of elements as values
    """
    grouped = {}
    
    for element in elements:
        if not element or not isinstance(element, dict):
            continue
            
        element_type = next(iter(element))
        
        if element_type not in grouped:
            grouped[element_type] = []
        
        grouped[element_type].append(element)
    
    return grouped


def create_extraction_summary(
    original_count: int, 
    extracted_count: int, 
    element_types: Set[str],
    grouped_data: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Create summary information about the extraction process.
    
    Args:
        original_count: Total number of elements in original document
        extracted_count: Number of elements extracted
        element_types: Set of requested element types
        grouped_data: Grouped extraction results
        
    Returns:
        Summary dictionary
    """
    type_counts = {element_type: len(elements) for element_type, elements in grouped_data.items()}
    
    return {
        'extraction_summary': {
            'total_elements_in_document': original_count,
            'total_elements_extracted': extracted_count,
            'extraction_rate': f"{(extracted_count/original_count)*100:.1f}%" if original_count > 0 else "0%",
            'requested_types': sorted(list(element_types)),
            'found_types': sorted(list(type_counts.keys())),
            'type_counts': type_counts
        }
    }


@click.command('extract')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--elements', '-e', multiple=True, 
              help=f'Element types to extract. Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES))}. Use "headers" for all header levels.')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', default='json', 
              type=click.Choice(['json']), help='Output format (currently only JSON supported)')
@click.option('--indent', type=int, default=2, help='JSON indentation level')
@click.option('--compact', is_flag=True, help='Use compact JSON format')
@click.option('--combine', is_flag=True, default=True, 
              help='Combine all extracted elements into single list (default: True)')
@click.option('--group-by-type', is_flag=True, 
              help='Group extracted elements by type instead of combining')
@click.option('--include-summary', is_flag=True, default=True,
              help='Include extraction summary in output (default: True)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def extract(ctx: click.Context, input_file: str, elements: tuple, output: Optional[str], 
           format: str, indent: int, compact: bool, combine: bool, group_by_type: bool,
           include_summary: bool, overwrite: bool, verbose: bool) -> None:
    """Extract specific elements from a markdown file.
    
    This command extracts specific markdown building blocks without full conversion.
    You can specify which elements to extract using the --elements option.
    
    Supported element types:
    - metadata: YAML frontmatter
    - header, h1, h2, h3, h4, h5, h6: Headers at specific levels
    - headers: All header levels
    - paragraph: Text paragraphs
    - list: Lists (ordered, unordered, task lists)
    - table: Tables
    - code: Code blocks
    - blockquote: Blockquotes
    - def_list: Definition lists
    - separator: Horizontal rules
    
    Examples:
        m2d extract document.md --elements "table code"
        m2d extract document.md --elements "h1 h2 paragraph" --group-by-type
        m2d extract document.md --elements "headers" --output headers.json
    """
    try:
        if verbose:
            console.print(f"📖 Extracting elements from: {input_file}", style="dim")
        
        # Validate input file
        validate_markdown_file(input_file)
        
        # Parse and validate element types
        target_elements = parse_element_types(elements)
        
        if verbose:
            console.print(f"🎯 Target elements: {', '.join(sorted(target_elements))}", style="dim")
        
        # Generate output path if not specified
        if not output:
            output = generate_output_path(input_file, output_extension='.json', suffix='_extracted')
        
        # Validate output path
        validate_output_path(output, overwrite)
        
        # Read and parse markdown
        content = read_markdown_file(input_file)
        md = Markdown(content)
        
        original_count = len(md.md_list)
        
        # Filter elements by type
        filtered_elements = filter_elements_by_type(md.md_list, target_elements)
        extracted_count = len(filtered_elements)
        
        if verbose:
            console.print(f"📊 Found {extracted_count} elements out of {original_count} total", style="dim")
        
        # Check if any elements were found
        if extracted_count == 0:
            if not ctx.obj.get('quiet', False):
                element_list = ', '.join(sorted(target_elements))
                console.print(f"⚠️  No elements of type(s) [{element_list}] found in {input_file}", style="yellow")
        
        # Prepare output data structure
        if group_by_type and not combine:
            # Group by element type
            grouped_data = group_elements_by_type(filtered_elements)
            output_data = grouped_data
        else:
            # Combined list format (default)
            output_data = filtered_elements
        
        # Add extraction summary if requested
        if include_summary and extracted_count > 0:
            grouped_for_summary = group_elements_by_type(filtered_elements)
            summary = create_extraction_summary(original_count, extracted_count, target_elements, grouped_for_summary)
            
            if isinstance(output_data, list):
                # For list format, add summary as first element
                output_data = [summary] + output_data
            else:
                # For grouped format, add summary as separate key
                output_data['extraction_summary'] = summary['extraction_summary']
        
        # Set indentation based on compact flag
        json_indent = None if compact else indent
        
        # Write JSON output
        write_json_file(output, output_data, json_indent)
        
        # Success message
        if not ctx.obj.get('quiet', False):
            if extracted_count > 0:
                console.print(f"✅ Extracted {extracted_count} elements: {input_file} → {output}", style="green")
            else:
                console.print(f"✅ Extraction completed (no matching elements): {input_file} → {output}", style="green")
            
            if verbose:
                if group_by_type and not combine:
                    grouped_data = group_elements_by_type(filtered_elements)
                    for element_type, type_elements in grouped_data.items():
                        console.print(f"  📋 {element_type}: {len(type_elements)} items", style="dim")
                else:
                    console.print(f"  📋 Total extracted elements: {extracted_count}", style="dim")
        
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Failed to extract elements from '{input_file}': {str(e)}")


@click.command('batch-extract')
@click.argument('pattern', default='**/*.md')
@click.option('--elements', '-e', multiple=True, 
              help=f'Element types to extract. Supported: {", ".join(sorted(SUPPORTED_ELEMENT_TYPES))}')
@click.option('--output-dir', type=click.Path(), help='Output directory for extracted data')
@click.option('--format', '-f', default='json', help='Output format (json)')
@click.option('--indent', type=int, default=2, help='JSON indentation level')
@click.option('--compact', is_flag=True, help='Use compact JSON format')
@click.option('--combine', is_flag=True, default=True, help='Combine all extracted elements into single list')
@click.option('--group-by-type', is_flag=True, help='Group extracted elements by type')
@click.option('--include-summary', is_flag=True, default=True, help='Include extraction summary in output')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively')
@click.option('--parallel', '-p', is_flag=True, help='Process files in parallel')
@click.option('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
@click.option('--aggregate', '-a', is_flag=True, help='Generate aggregated extraction results')
@click.option('--preserve-structure', is_flag=True, help='Preserve directory structure in output')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--continue-on-error', is_flag=True, help='Continue processing if individual files fail')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_extract(ctx: click.Context, pattern: str, elements: tuple, output_dir: Optional[str],
                 format: str, indent: int, compact: bool, combine: bool, group_by_type: bool,
                 include_summary: bool, recursive: bool, parallel: bool, max_workers: int,
                 aggregate: bool, preserve_structure: bool, overwrite: bool, 
                 continue_on_error: bool, verbose: bool) -> None:
    """
    Extract specific elements from multiple markdown files.
    
    PATTERN specifies the file pattern to search for (default: **/*.md).
    Supports glob patterns like '*.md', 'docs/**/*.md', etc.
    
    Examples:
    
        # Extract tables from all markdown files
        m2d batch-extract --elements "table"
        
        # Extract headers and lists with output directory
        m2d batch-extract "docs/**/*.md" --elements "headers list" --output-dir extracted
        
        # Extract with parallel processing and aggregation
        m2d batch-extract --elements "table code" --parallel --aggregate --output-dir results
        
        # Extract and group by type
        m2d batch-extract --elements "h1 h2 paragraph" --group-by-type --output-dir results
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
        
        # Validate elements argument
        if not elements:
            raise CLIError("No element types specified. Use --elements to specify what to extract.")
            
        # Parse and validate element types
        element_types = parse_element_types(elements)
        
        # Find files to process
        files = find_files_for_batch(pattern, recursive=recursive)
        
        if not files:
            console.print(f"❌ No files found matching pattern: {pattern}", style="red")
            return
            
        if verbose:
            console.print(f"📁 Found {len(files)} files to process", style="blue")
            console.print(f"🎯 Extracting element types: {', '.join(sorted(element_types))}", style="blue")
            
        # Create output directory if specified
        if output_dir:
            create_batch_output_directory(output_dir, overwrite=overwrite)
        else:
            output_dir = "."
            
        # Define processing function for batch processor
        def process_single_file(file_path: str) -> Dict[str, Any]:
            """Process a single file and return extraction result."""
            try:
                # Load markdown
                md = Markdown(file_path)
                
                # Filter elements by type
                filtered_data = filter_elements_by_type(md.md_list, element_types)
                
                # Group by type if requested (only for individual files, not aggregate)
                if group_by_type and not aggregate:
                    result_data = group_elements_by_type(filtered_data)
                else:
                    result_data = filtered_data
                
                # Create extraction summary if requested
                extraction_summary = None
                if include_summary:
                    extraction_summary = create_extraction_summary(
                        original_data=md.md_list,
                        filtered_data=filtered_data,
                        element_types=element_types
                    )
                
                # Prepare final output
                output_data = {
                    'extracted_elements': result_data
                }
                
                if include_summary:
                    output_data['extraction_summary'] = extraction_summary
                
                # Determine output filename
                input_path = Path(file_path)
                
                if preserve_structure:
                    # Preserve relative directory structure
                    relative_path = input_path.relative_to(Path.cwd())
                    output_file = Path(output_dir) / relative_path.with_suffix('.extracted.json')
                    # Ensure parent directories exist
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flatten to output directory
                    output_file = Path(output_dir) / f"{input_path.stem}.extracted.json"
                
                # Write JSON file
                write_json_file(
                    str(output_file),
                    output_data,
                    indent=None if compact else indent
                )
                
                # Return result info
                extracted_count = len(filtered_data)
                
                return {
                    'input_file': file_path,
                    'output_file': str(output_file),
                    'element_types': sorted(list(element_types)),
                    'extracted_count': extracted_count,
                    'extracted_elements': filtered_data,  # For aggregation
                    'extraction_summary': extraction_summary,
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
            task_name="element extraction",
            max_workers=max_workers if parallel else 1,
            show_progress=not ctx.obj.get('quiet', False)
        )
        
        # Process files
        with console.status("[bold blue]Extracting elements...") if ctx.obj.get('quiet', False) else nullcontext():
            result = processor.process_files(files, process_single_file)
            
        # Handle successful extractions
        if result.successes:
            # Calculate statistics
            total_extracted = sum(
                success['result'].get('extracted_count', 0) 
                for success in result.successes 
                if 'extracted_count' in success['result']
            )
            total_size = sum(
                success['result'].get('file_size', 0)
                for success in result.successes
                if 'file_size' in success['result']
            )
            
            if verbose:
                console.print(f"📊 Extracted {total_extracted} total elements", style="dim")
                console.print(f"💾 Generated {format_file_size(total_size)} of extracted data", style="dim")
            
            # Generate aggregated results if requested
            if aggregate and output_dir:
                aggregated_data = create_aggregated_extraction_results(
                    result.successes, element_types, group_by_type
                )
                aggregate_file = Path(output_dir) / "aggregated_extractions.json"
                
                try:
                    write_json_file(
                        str(aggregate_file), 
                        aggregated_data, 
                        indent=None if compact else indent
                    )
                    if not ctx.obj.get('quiet', False):
                        console.print(f"📊 Aggregated extractions saved to: {aggregate_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save aggregated extractions: {e}", style="red")
                    
        # Print summary
        if not ctx.obj.get('quiet', False):
            print_batch_summary(result, "Element extraction")
            
        # Handle errors
        if result.errors:
            error_collector = BatchErrorCollector()
            for error in result.errors:
                error_collector.add_error(error['file'], error['error'])
                
            if not continue_on_error:
                console.print(f"\n❌ {len(result.errors)} files failed to process", style="red")
                error_collector.print_error_summary()
                
            # Save error log if output directory specified
            if output_dir:
                error_log_file = Path(output_dir) / "extraction_errors.txt"
                error_collector.save_error_log(str(error_log_file))
                if verbose:
                    console.print(f"📝 Error log saved to: {error_log_file}", style="yellow")
                    
        if verbose:
            console.print(f"✅ Batch extraction completed: {len(result.successes)} successful, {len(result.errors)} failed", style="green")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Batch extraction failed: {str(e)}")


def create_aggregated_extraction_results(successes: List[Dict[str, Any]], 
                                       element_types: Set[str], 
                                       group_by_type: bool) -> Dict[str, Any]:
    """Create aggregated extraction results from all processed files."""
    if not successes:
        return {}
        
    aggregated = {
        'summary': {
            'total_files': len(successes),
            'processed_at': datetime.now().isoformat(),
            'element_types_requested': sorted(list(element_types)),
        },
        'statistics': {
            'total_elements_extracted': 0,
            'elements_per_file': {},
            'element_type_counts': {},
        },
    }
    
    # Collect all extracted elements
    all_elements = []
    
    for success in successes:
        result = success['result']
        
        # Skip error files
        if 'error' in result:
            continue
            
        file_path = result.get('input_file', '')
        extracted_count = result.get('extracted_count', 0)
        extracted_elements = result.get('extracted_elements', [])
        
        # Update statistics
        aggregated['statistics']['total_elements_extracted'] += extracted_count
        aggregated['statistics']['elements_per_file'][file_path] = extracted_count
        
        # Add elements to aggregated collection
        all_elements.extend(extracted_elements)
        
        # Count element types
        for element in extracted_elements:
            if isinstance(element, dict):
                element_type = next(iter(element.keys()))
                aggregated['statistics']['element_type_counts'][element_type] = \
                    aggregated['statistics']['element_type_counts'].get(element_type, 0) + 1
    
    # Organize extracted elements
    if group_by_type:
        aggregated['extracted_elements'] = group_elements_by_type(all_elements)
    else:
        aggregated['extracted_elements'] = all_elements
        
    return aggregated


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"