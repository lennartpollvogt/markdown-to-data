"""
Info command implementations for markdown-to-data CLI tool.

This module provides the 'info' and 'batch-info' commands for extracting
metadata and structural information from markdown files.
"""

import click
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

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
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_info(ctx: click.Context, pattern: str, output_dir: Optional[str], format: str, recursive: bool, verbose: bool) -> None:
    """Extract information from multiple markdown files."""
    # TODO: Implement in Phase 4
    raise NotImplementedError("The 'batch-info' command will be implemented in Phase 4")