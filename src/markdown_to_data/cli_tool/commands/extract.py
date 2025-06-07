"""
Extract command implementations for markdown-to-data CLI tool.

This module provides the 'extract' and 'batch-extract' commands for extracting
specific elements from markdown files.
"""

import click
from typing import Optional, List, Dict, Any, Set, Union

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
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_extract(ctx: click.Context, pattern: str, elements: tuple, output_dir: Optional[str],
                 format: str, indent: int, compact: bool, combine: bool, group_by_type: bool,
                 include_summary: bool, recursive: bool, overwrite: bool, verbose: bool) -> None:
    """Extract specific elements from multiple markdown files."""
    # TODO: Implement in Phase 4
    raise NotImplementedError("The 'batch-extract' command will be implemented in Phase 4")