"""
Info command implementations for markdown-to-data CLI tool.

This module provides the 'info' and 'batch-info' commands for extracting
metadata and structural information from markdown files.
"""

import click
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from contextlib import nullcontext

from markdown_to_data import Markdown
from ..utils.constants import COMMAND_DESCRIPTIONS, SUPPORTED_ELEMENT_TYPES
from ..utils.error_utils import CLIError, validate_markdown_file, handle_cli_error
from ..utils.file_utils import read_markdown_file, write_json_file, get_file_info
from ..utils.format_utils import (
    create_info_table, create_metadata_display, create_element_summary_table,
    print_json_output, console
)


def extract_file_info(filepath: str, include_options: List[str] = None) -> Dict[str, Any]:
    """
    Extract comprehensive information from a markdown file.
    
    Args:
        filepath: Path to the markdown file
        include_options: List of info types to include
        
    Returns:
        Dictionary containing file information
    """
    if include_options is None:
        include_options = ['metadata', 'toc', 'words', 'blocks']
    
    # Read and parse the markdown file
    content = read_markdown_file(filepath)
    md = Markdown(content)
    
    info = {
        'file': str(Path(filepath).name),
        'filepath': filepath
    }
    
    # Extract metadata
    if 'metadata' in include_options:
        metadata = {}
        for element in md.md_list:
            if 'metadata' in element:
                metadata = element['metadata']
                break
        info['metadata'] = metadata
    
    # Extract table of contents (headers)
    if 'toc' in include_options:
        toc = []
        for element in md.md_list:
            if 'header' in element:
                header_data = element['header']
                level = header_data['level']
                content = header_data['content']
                toc.append({
                    'level': level,
                    'content': content,
                    'indent': '  ' * (level - 1)
                })
        info['table_of_content'] = toc
    
    # Count words (excluding metadata and symbols)
    if 'words' in include_options:
        word_count = 0
        for element in md.md_list:
            if 'paragraph' in element:
                # Count words in paragraphs
                text = element['paragraph']
                words = re.findall(r'\b\w+\b', text)
                word_count += len(words)
            elif 'header' in element:
                # Count words in headers
                text = element['header']['content']
                words = re.findall(r'\b\w+\b', text)
                word_count += len(words)
            elif 'list' in element:
                # Count words in list items
                def count_list_words(items):
                    count = 0
                    for item in items:
                        text = item.get('content', '')
                        words = re.findall(r'\b\w+\b', text)
                        count += len(words)
                        count += count_list_words(item.get('items', []))
                    return count
                word_count += count_list_words(element['list'].get('items', []))
        
        info['word_count'] = word_count
    
    # Extract building blocks summary
    if 'blocks' in include_options:
        elements_info = md.md_elements
        blocks_summary = {}
        
        for element_type, element_data in elements_info.items():
            count = element_data.get('count', 0)
            if count > 0:
                if element_type == 'header':
                    # Show header levels
                    levels = element_data.get('summary', {}).get('levels', {})
                    for level, level_count in levels.items():
                        blocks_summary[f'h{level}'] = level_count
                else:
                    blocks_summary[element_type] = count
        
        info['blocks'] = blocks_summary
    
    return info


def format_info_display(info: Dict[str, Any], format_type: str = 'table') -> None:
    """
    Display file information in the specified format.
    
    Args:
        info: Information dictionary
        format_type: Display format ('table' or 'json')
    """
    if format_type == 'json':
        print_json_output(info)
        return
    
    # Display as formatted table
    filename = info.get('file', 'Unknown')
    console.print(f"\n📄 File Information: {filename}", style="bold blue")
    
    # Show metadata if present
    if 'metadata' in info and info['metadata']:
        metadata_panel = create_metadata_display(info['metadata'])
        console.print(metadata_panel)
    
    # Show table of contents
    if 'table_of_content' in info and info['table_of_content']:
        console.print("\n📋 Table of Contents:", style="bold cyan")
        for header in info['table_of_content']:
            level_indicator = "│  " * (header['level'] - 1) + "├─ " if header['level'] > 1 else ""
            console.print(f"  {level_indicator}H{header['level']}: {header['content']}")
    
    # Show word count
    if 'word_count' in info:
        console.print(f"\n📊 Word Count: {info['word_count']} words", style="bold green")
    
    # Show building blocks summary
    if 'blocks' in info and info['blocks']:
        console.print("\n🧱 Building Blocks:", style="bold yellow")
        for block_type, count in info['blocks'].items():
            icon = {
                'h1': '📍', 'h2': '📌', 'h3': '📎', 'h4': '📄', 'h5': '📝', 'h6': '📋',
                'paragraph': '📄', 'list': '📝', 'table': '📊', 'code': '💻',
                'blockquote': '💬', 'metadata': '📋', 'def_list': '📚'
            }.get(block_type, '❓')
            console.print(f"  {icon} {block_type}: {count}")


@click.command('info')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--include', help='Information types to include: metadata, toc, words, blocks (default: all)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (JSON format)')
@click.option('--format', '-f', default='table', help='Output format (table, json)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def info(ctx: click.Context, input_file: str, include: Optional[str], output: Optional[str], 
         format: str, verbose: bool) -> None:
    """Extract metadata and structural information from a markdown file.
    
    This command analyzes a markdown file and extracts various types of information:
    
    - metadata: YAML frontmatter (title, author, tags, etc.)
    - toc: Table of contents (header structure)  
    - words: Word count (excluding metadata and symbols)
    - blocks: Summary of markdown elements (headers, lists, tables, etc.)
    
    Examples:
        m2d info document.md
        m2d info document.md --include "metadata toc"
        m2d info document.md --format json --output info.json
    """
    try:
        # Parse include options
        include_options = ['metadata', 'toc', 'words', 'blocks']  # Default: all
        if include:
            include_options = include.strip().split()
            # Validate include options
            valid_options = ['metadata', 'toc', 'words', 'blocks']
            for option in include_options:
                if option not in valid_options:
                    raise CLIError(f"Invalid include option '{option}'. Valid options: {', '.join(valid_options)}")
        
        if verbose:
            console.print(f"📖 Analyzing file: {input_file}", style="dim")
        
        # Extract file information
        info = extract_file_info(input_file, include_options)
        
        # Save to output file if specified
        if output:
            write_json_file(output, info)
            if not ctx.obj.get('quiet', False):
                console.print(f"✅ Information saved to: {output}", style="green")
        
        # Display information
        if not ctx.obj.get('quiet', False):
            format_info_display(info, format)
        
        if verbose:
            console.print(f"✅ Successfully analyzed file: {input_file}", style="green")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Failed to analyze file '{input_file}': {str(e)}")


@click.command('batch-info')
@click.argument('pattern', default='**/*.md')
@click.option('--output-dir', type=click.Path(), help='Output directory for results')
@click.option('--format', '-f', default='json', help='Output format')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively')
@click.option('--parallel', '-p', is_flag=True, help='Process files in parallel')
@click.option('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
@click.option('--aggregate', '-a', is_flag=True, help='Generate aggregated summary')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--continue-on-error', is_flag=True, help='Continue processing if individual files fail')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_info(ctx: click.Context, pattern: str, output_dir: Optional[str], format: str, recursive: bool, 
               parallel: bool, max_workers: int, aggregate: bool, overwrite: bool, 
               continue_on_error: bool, verbose: bool) -> None:
    """
    Extract information from multiple markdown files.
    
    PATTERN specifies the file pattern to search for (default: **/*.md).
    Supports glob patterns like '*.md', 'docs/**/*.md', etc.
    
    Examples:
    
        # Process all markdown files in current directory and subdirectories
        m2d batch-info
        
        # Process specific pattern with output directory
        m2d batch-info "docs/**/*.md" --output-dir results
        
        # Process with parallel execution and aggregation
        m2d batch-info --parallel --aggregate --output-dir results
        
        # Process with custom worker count
        m2d batch-info --parallel --max-workers 8
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
        
        # Find files to process
        files = find_files_for_batch(pattern, recursive=recursive)
        
        if not files:
            console.print(f"❌ No files found matching pattern: {pattern}", style="red")
            return
            
        if verbose:
            console.print(f"📁 Found {len(files)} files to process", style="blue")
            
        # Create output directory if specified
        if output_dir:
            create_batch_output_directory(output_dir, overwrite=overwrite)
            
        # Define processing function for batch processor
        def process_single_file(file_path: str) -> Dict[str, Any]:
            """Process a single file and return its info."""
            try:
                # Use the same logic as the single info command
                info = extract_file_info(file_path, {
                    'metadata': True,
                    'headers': True,
                    'elements': True,
                    'statistics': True
                })
                
                # Add file path to the result
                info['file_path'] = file_path
                return info
                
            except Exception as e:
                if not continue_on_error:
                    raise
                # Return error info for failed files
                return {
                    'file_path': file_path,
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Set up batch processor
        processor = BatchProcessor(
            task_name="info extraction",
            max_workers=max_workers if parallel else 1,
            show_progress=not ctx.obj.get('quiet', False)
        )
        
        # Process files
        with console.status("[bold blue]Processing files...") if ctx.obj.get('quiet', False) else nullcontext():
            result = processor.process_files(files, process_single_file)
            
        # Handle results
        if output_dir:
            # Save individual results
            for success in result.successes:
                file_info = success['result']
                file_path = file_info['file_path']
                
                # Create relative path for output filename
                relative_path = Path(file_path).name
                output_file = Path(output_dir) / f"{relative_path}.info.json"
                
                try:
                    write_json_file(str(output_file), file_info)
                    if verbose:
                        console.print(f"💾 Saved: {output_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save {output_file}: {e}", style="red")
            
            # Save aggregated results if requested
            if aggregate:
                aggregated_data = create_aggregated_info_summary(result.successes)
                aggregate_file = Path(output_dir) / "aggregated_info.json"
                
                try:
                    write_json_file(str(aggregate_file), aggregated_data)
                    if not ctx.obj.get('quiet', False):
                        console.print(f"📊 Aggregated summary saved to: {aggregate_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save aggregated summary: {e}", style="red")
                    
        # Print summary
        if not ctx.obj.get('quiet', False):
            print_batch_summary(result, "Information extraction")
            
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
                error_log_file = Path(output_dir) / "error_log.txt"
                error_collector.save_error_log(str(error_log_file))
                if verbose:
                    console.print(f"📝 Error log saved to: {error_log_file}", style="yellow")
                    
        if verbose:
            console.print(f"✅ Batch processing completed: {len(result.successes)} successful, {len(result.errors)} failed", style="green")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Batch info processing failed: {str(e)}")


def create_aggregated_info_summary(successes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create an aggregated summary of all processed files."""
    if not successes:
        return {}
        
    aggregated = {
        'summary': {
            'total_files': len(successes),
            'processed_at': datetime.now().isoformat(),
        },
        'global_statistics': {
            'total_headers': 0,
            'total_elements': 0,
            'header_levels': {},
            'element_types': {},
            'files_with_metadata': 0,
            'files_with_headers': 0,
        },
        'files': []
    }
    
    # Aggregate statistics
    for success in successes:
        file_info = success['result']
        
        # Skip error files
        if 'error' in file_info:
            continue
            
        # Add file summary
        file_summary = {
            'file_path': file_info.get('file_path', ''),
            'has_metadata': bool(file_info.get('metadata')),
            'header_count': len(file_info.get('headers', [])),
            'element_count': sum(info.get('count', 0) for info in file_info.get('elements', {}).values())
        }
        aggregated['files'].append(file_summary)
        
        # Update global statistics
        if file_info.get('metadata'):
            aggregated['global_statistics']['files_with_metadata'] += 1
            
        headers = file_info.get('headers', [])
        if headers:
            aggregated['global_statistics']['files_with_headers'] += 1
            aggregated['global_statistics']['total_headers'] += len(headers)
            
            # Count header levels
            for header in headers:
                level = header.get('level', 1)
                level_key = f'h{level}'
                aggregated['global_statistics']['header_levels'][level_key] = \
                    aggregated['global_statistics']['header_levels'].get(level_key, 0) + 1
                    
        # Count element types
        elements = file_info.get('elements', {})
        for element_type, element_info in elements.items():
            count = element_info.get('count', 0)
            aggregated['global_statistics']['total_elements'] += count
            aggregated['global_statistics']['element_types'][element_type] = \
                aggregated['global_statistics']['element_types'].get(element_type, 0) + count
                
    return aggregated