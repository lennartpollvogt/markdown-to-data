"""
Search command implementation for markdown-to-data CLI tool.

This module provides the 'search' command for searching content within
markdown files with various filtering and display options.
"""

import re
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Union, Tuple
from dataclasses import dataclass

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.highlighter import RegexHighlighter
from rich.syntax import Syntax

from markdown_to_data import Markdown
from ..utils.constants import (
    SUPPORTED_ELEMENT_TYPES, SEARCH_SETTINGS, MARKDOWN_EXTENSIONS,
    DEFAULT_EXCLUDE_PATTERNS
)
from ..utils.error_utils import CLIError, validate_markdown_file
from ..utils.file_utils import find_markdown_files, read_markdown_file
from ..utils.format_utils import console

console = Console()


@dataclass
class SearchMatch:
    """Represents a search match within a markdown file."""
    filepath: str
    element_type: str
    element_index: int
    content: str
    line_number: Optional[int] = None
    context_before: Optional[List[str]] = None
    context_after: Optional[List[str]] = None
    match_positions: Optional[List[Tuple[int, int]]] = None


@dataclass
class SearchResult:
    """Results of a search operation."""
    query: str
    total_files: int
    files_with_matches: int
    total_matches: int
    matches: List[SearchMatch]
    errors: List[Tuple[str, str]]


class MarkdownSearchHighlighter(RegexHighlighter):
    """Custom highlighter for search matches."""
    
    def __init__(self, pattern: str, case_sensitive: bool = False):
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            self.search_pattern = re.compile(pattern, flags)
        except re.error:
            # Fallback to literal string search if regex is invalid
            escaped_pattern = re.escape(pattern)
            self.search_pattern = re.compile(escaped_pattern, flags)
    
    def highlight(self, text: Text) -> None:
        """Highlight search matches in text."""
        for match in self.search_pattern.finditer(str(text)):
            start, end = match.span()
            text.stylize("bold yellow on red", start, end)


def parse_element_types(element_types: tuple) -> Set[str]:
    """
    Parse and validate element types for search filtering.
    
    Args:
        element_types: Tuple of element type strings
        
    Returns:
        Set of validated element types, or empty set for all types
    """
    if not element_types:
        return set()  # Empty set means search all element types
    
    # Flatten space-separated element lists
    parsed_elements = set()
    for element_group in element_types:
        for element in element_group.split():
            element = element.strip().lower()
            if element:
                parsed_elements.add(element)
    
    # Expand aliases
    if 'headers' in parsed_elements:
        parsed_elements.remove('headers')
        parsed_elements.update(['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    # Validate element types
    invalid_elements = [e for e in parsed_elements if e not in SUPPORTED_ELEMENT_TYPES]
    if invalid_elements:
        supported_types_str = ', '.join(sorted(SUPPORTED_ELEMENT_TYPES))
        raise CLIError(
            f"Invalid element type(s): {', '.join(invalid_elements)}. "
            f"Supported types: {supported_types_str}"
        )
    
    return parsed_elements


def search_in_element(
    element: Dict[str, Any], 
    pattern: str, 
    regex: bool = False, 
    case_sensitive: bool = False
) -> List[Tuple[int, int]]:
    """
    Search for pattern within a markdown element.
    
    Args:
        element: Markdown element dictionary
        pattern: Search pattern
        regex: Whether to use regex matching
        case_sensitive: Whether search is case sensitive
        
    Returns:
        List of match positions (start, end) within the element content
    """
    # Extract searchable text from element
    searchable_text = extract_element_text(element)
    if not searchable_text:
        return []
    
    # Prepare search pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    
    try:
        if regex:
            search_pattern = re.compile(pattern, flags)
        else:
            # Escape special regex characters for literal search
            escaped_pattern = re.escape(pattern)
            search_pattern = re.compile(escaped_pattern, flags)
    except re.error as e:
        raise CLIError(f"Invalid search pattern '{pattern}': {str(e)}")
    
    # Find all matches
    matches = []
    for match in search_pattern.finditer(searchable_text):
        matches.append(match.span())
    
    return matches


def extract_element_text(element: Dict[str, Any]) -> str:
    """
    Extract searchable text from a markdown element.
    
    Args:
        element: Markdown element dictionary
        
    Returns:
        Concatenated text content from the element
    """
    element_type = next(iter(element))
    element_data = element[element_type]
    
    if element_type == 'header':
        return element_data.get('content', '')
    
    elif element_type == 'paragraph':
        return element_data
    
    elif element_type == 'list':
        text_parts = []
        items = element_data.get('items', [])
        for item in items:
            text_parts.append(extract_list_item_text(item))
        return ' '.join(text_parts)
    
    elif element_type == 'table':
        text_parts = []
        for column, values in element_data.items():
            text_parts.append(column)  # Include column headers
            text_parts.extend(values)
        return ' '.join(text_parts)
    
    elif element_type == 'code':
        content = element_data.get('content', '')
        language = element_data.get('language', '')
        return f"{language} {content}"
    
    elif element_type == 'blockquote':
        text_parts = []
        for quote_item in element_data:
            text_parts.append(quote_item.get('content', ''))
            # Recursively extract from nested items
            for nested_item in quote_item.get('items', []):
                text_parts.append(extract_blockquote_item_text(nested_item))
        return ' '.join(text_parts)
    
    elif element_type == 'def_list':
        term = element_data.get('term', '')
        definitions = element_data.get('list', [])
        return f"{term} {' '.join(definitions)}"
    
    elif element_type == 'metadata':
        # Convert metadata to searchable text
        text_parts = []
        for key, value in element_data.items():
            text_parts.append(f"{key}: {value}")
        return ' '.join(text_parts)
    
    return ''


def extract_list_item_text(item: Dict[str, Any]) -> str:
    """Extract text from a list item recursively."""
    text_parts = [item.get('content', '')]
    
    # Process nested items
    for nested_item in item.get('items', []):
        text_parts.append(extract_list_item_text(nested_item))
    
    return ' '.join(text_parts)


def extract_blockquote_item_text(item: Dict[str, Any]) -> str:
    """Extract text from a blockquote item recursively."""
    text_parts = [item.get('content', '')]
    
    # Process nested items
    for nested_item in item.get('items', []):
        text_parts.append(extract_blockquote_item_text(nested_item))
    
    return ' '.join(text_parts)


def search_markdown_file(
    filepath: str,
    pattern: str,
    element_types: Set[str],
    regex: bool = False,
    case_sensitive: bool = False,
    max_results: int = None
) -> List[SearchMatch]:
    """
    Search for pattern within a single markdown file.
    
    Args:
        filepath: Path to markdown file
        pattern: Search pattern
        element_types: Set of element types to search (empty for all)
        regex: Whether to use regex matching
        case_sensitive: Whether search is case sensitive
        max_results: Maximum number of results to return
        
    Returns:
        List of search matches
    """
    try:
        # Parse markdown file
        content = read_markdown_file(filepath)
        md = Markdown(content)
        
        matches = []
        
        # Search through each element
        for i, element in enumerate(md.md_list):
            element_type = next(iter(element))
            
            # Skip if element type not in filter (when filter is specified)
            if element_types and element_type not in element_types:
                continue
            
            # Search within element
            match_positions = search_in_element(element, pattern, regex, case_sensitive)
            
            if match_positions:
                # Extract element text for display
                element_text = extract_element_text(element)
                
                match = SearchMatch(
                    filepath=filepath,
                    element_type=element_type,
                    element_index=i,
                    content=element_text,
                    match_positions=match_positions
                )
                matches.append(match)
                
                # Check max results limit
                if max_results and len(matches) >= max_results:
                    break
        
        return matches
        
    except Exception as e:
        raise CLIError(f"Failed to search file '{filepath}': {str(e)}")


def format_search_results(
    result: SearchResult,
    format_type: str = 'table',
    highlight: bool = True,
    line_numbers: bool = False,
    files_only: bool = False,
    count_only: bool = False
) -> None:
    """
    Format and display search results.
    
    Args:
        result: Search results to display
        format_type: Output format ('table', 'list', 'json')
        highlight: Whether to highlight matches
        line_numbers: Whether to show line numbers
        files_only: Show only filenames with matches
        count_only: Show only match counts
    """
    if not result.matches:
        console.print("🔍 No matches found.", style="yellow")
        return
    
    # Count matches per file
    file_match_counts = {}
    for match in result.matches:
        if match.filepath not in file_match_counts:
            file_match_counts[match.filepath] = 0
        file_match_counts[match.filepath] += 1
    
    # Display header
    console.print(f"\n🔍 Search Results for: [bold cyan]'{result.query}'[/bold cyan]")
    console.print(f"📁 Files searched: {result.total_files}")
    console.print(f"📄 Files with matches: {result.files_with_matches}")
    console.print(f"🎯 Total matches: {result.total_matches}\n")
    
    if count_only:
        # Show only counts per file
        table = Table(title="Match Counts")
        table.add_column("File", style="cyan")
        table.add_column("Matches", style="green", justify="right")
        
        for filepath, count in sorted(file_match_counts.items()):
            table.add_row(os.path.basename(filepath), str(count))
        
        console.print(table)
        return
    
    if files_only:
        # Show only filenames
        console.print("📁 Files with matches:")
        for filepath in sorted(file_match_counts.keys()):
            count = file_match_counts[filepath]
            console.print(f"  • {filepath} ([green]{count}[/green] matches)")
        return
    
    if format_type == 'json':
        # JSON output
        json_data = {
            'query': result.query,
            'summary': {
                'total_files': result.total_files,
                'files_with_matches': result.files_with_matches,
                'total_matches': result.total_matches
            },
            'matches': [
                {
                    'file': match.filepath,
                    'element_type': match.element_type,
                    'element_index': match.element_index,
                    'content': match.content,
                    'match_count': len(match.match_positions) if match.match_positions else 1
                }
                for match in result.matches
            ]
        }
        console.print(json.dumps(json_data, indent=2))
        return
    
    # Table or list format
    if format_type == 'table':
        table = Table(title="Search Matches", show_lines=True)
        table.add_column("File", style="cyan", width=30)
        table.add_column("Element", style="magenta", width=12)
        table.add_column("Content", style="white", width=60)
        
        highlighter = MarkdownSearchHighlighter(result.query, case_sensitive=False) if highlight else None
        
        for match in result.matches[:50]:  # Limit display to first 50 matches
            filename = os.path.basename(match.filepath)
            element_info = f"{match.element_type} #{match.element_index}"
            
            # Truncate content if too long
            content = match.content
            if len(content) > 200:
                content = content[:200] + "..."
            
            if highlight and highlighter:
                content_text = Text(content)
                highlighter.highlight(content_text)
                table.add_row(filename, element_info, content_text)
            else:
                table.add_row(filename, element_info, content)
        
        console.print(table)
        
        if len(result.matches) > 50:
            console.print(f"\n... and {len(result.matches) - 50} more matches (use --max-results to see more)")
    
    else:  # list format
        highlighter = MarkdownSearchHighlighter(result.query, case_sensitive=False) if highlight else None
        
        current_file = None
        for match in result.matches[:50]:
            if match.filepath != current_file:
                current_file = match.filepath
                console.print(f"\n📄 [bold cyan]{match.filepath}[/bold cyan]")
            
            element_info = f"  🔹 {match.element_type} #{match.element_index}"
            console.print(element_info)
            
            # Show content with highlighting
            content = match.content
            if len(content) > 300:
                content = content[:300] + "..."
            
            if highlight and highlighter:
                content_text = Text(f"     {content}")
                highlighter.highlight(content_text)
                console.print(content_text)
            else:
                console.print(f"     {content}")


@click.command('search')
@click.argument('pattern')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--element-type', '-e', multiple=True, 
              help=f'Search only in specific element types. Supported: {", ".join(SUPPORTED_ELEMENT_TYPES)}')
@click.option('--case-sensitive', is_flag=True, help='Case-sensitive search')
@click.option('--regex', is_flag=True, help='Use regular expression pattern')
@click.option('--max-results', type=int, default=SEARCH_SETTINGS['max_results'], 
              help='Maximum number of results to show per file')
@click.option('--recursive', '-r', is_flag=True, help='Search recursively in directories')
@click.option('--output', '-o', type=click.Path(), help='Output file for search results')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'list']),
              help='Output format')
@click.option('--highlight/--no-highlight', default=True, help='Highlight search matches')
@click.option('--files-only', is_flag=True, help='Show only filenames with matches')
@click.option('--count-only', is_flag=True, help='Show only count of matches per file')
@click.option('--include-pattern', multiple=True, help='File patterns to include (glob)')
@click.option('--exclude-pattern', multiple=True, help='File patterns to exclude (glob)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def search(ctx: click.Context, pattern: str, files: tuple, element_type: tuple, 
          case_sensitive: bool, regex: bool, max_results: int, recursive: bool, 
          output: Optional[str], format: str, highlight: bool, files_only: bool, 
          count_only: bool, include_pattern: tuple, exclude_pattern: tuple, 
          verbose: bool) -> None:
    """
    Search for content within markdown files.
    
    PATTERN: Search pattern or query string
    FILES: Markdown files to search (if not provided, searches current directory)
    
    Examples:
        # Search for "TODO" in a specific file
        m2d search "TODO" document.md
        
        # Search for headers containing "Chapter"
        m2d search "Chapter" --element-type header docs/
        
        # Case-sensitive regex search
        m2d search "^#+ " --regex --case-sensitive --recursive .
        
        # Search and output to JSON
        m2d search "Python" --format json --output results.json
        
        # Show only file names with matches
        m2d search "TODO" --files-only --recursive .
    """
    try:
        if verbose:
            console.print(f"🔍 Searching for pattern: '{pattern}'", style="dim")
        
        # Parse element types filter
        target_element_types = parse_element_types(element_type)
        
        if verbose and target_element_types:
            console.print(f"🎯 Filtering elements: {', '.join(sorted(target_element_types))}", style="dim")
        
        # Determine files to search
        if files:
            # Use provided files/directories
            search_files = []
            for file_path in files:
                if os.path.isfile(file_path):
                    # Validate markdown file
                    try:
                        validate_markdown_file(file_path)
                        search_files.append(file_path)
                    except CLIError as e:
                        if verbose:
                            console.print(f"⚠️ Skipping {file_path}: {e.message}", style="yellow")
                        continue
                elif os.path.isdir(file_path):
                    # Find markdown files in directory
                    dir_files = find_markdown_files(
                        file_path, 
                        recursive=recursive,
                        include_patterns=include_pattern or ('**/*.md',),
                        exclude_patterns=exclude_pattern or DEFAULT_EXCLUDE_PATTERNS
                    )
                    search_files.extend(dir_files)
                else:
                    console.print(f"⚠️ Path not found: {file_path}", style="yellow")
        else:
            # Search current directory
            search_files = find_markdown_files(
                '.',
                recursive=recursive,
                include_patterns=include_pattern or ('**/*.md',),
                exclude_patterns=exclude_pattern or DEFAULT_EXCLUDE_PATTERNS
            )
        
        if not search_files:
            console.print("❌ No markdown files found to search.", style="red")
            return
        
        if verbose:
            console.print(f"📁 Found {len(search_files)} markdown files to search", style="dim")
        
        # Perform search
        all_matches = []
        files_with_matches = 0
        search_errors = []
        
        with console.status("[bold green]Searching files...") as status:
            for i, filepath in enumerate(search_files):
                if verbose:
                    status.update(f"[bold green]Searching... {os.path.basename(filepath)} ({i+1}/{len(search_files)})")
                
                try:
                    matches = search_markdown_file(
                        filepath, 
                        pattern, 
                        target_element_types, 
                        regex, 
                        case_sensitive, 
                        max_results
                    )
                    
                    if matches:
                        all_matches.extend(matches)
                        files_with_matches += 1
                        
                except CLIError as e:
                    search_errors.append((filepath, str(e)))
                    if verbose:
                        console.print(f"⚠️ Error searching {filepath}: {e.message}", style="yellow")
        
        # Create search result
        result = SearchResult(
            query=pattern,
            total_files=len(search_files),
            files_with_matches=files_with_matches,
            total_matches=len(all_matches),
            matches=all_matches,
            errors=search_errors
        )
        
        # Output results
        if output:
            # Save to file
            if format == 'json':
                json_data = {
                    'query': result.query,
                    'summary': {
                        'total_files': result.total_files,
                        'files_with_matches': result.files_with_matches,
                        'total_matches': result.total_matches
                    },
                    'matches': [
                        {
                            'file': match.filepath,
                            'element_type': match.element_type,
                            'element_index': match.element_index,
                            'content': match.content,
                            'match_count': len(match.match_positions) if match.match_positions else 1
                        }
                        for match in result.matches
                    ],
                    'errors': [{'file': f, 'error': e} for f, e in result.errors]
                }
                
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                
                console.print(f"💾 Search results saved to: {output}")
            else:
                console.print(f"⚠️ File output only supported for JSON format", style="yellow")
        
        # Display results
        format_search_results(
            result, 
            format_type=format, 
            highlight=highlight, 
            files_only=files_only, 
            count_only=count_only
        )
        
        # Show errors if any
        if search_errors and verbose:
            console.print(f"\n⚠️ {len(search_errors)} files had search errors:", style="yellow")
            for filepath, error in search_errors[:5]:  # Show first 5 errors
                console.print(f"  • {filepath}: {error}", style="dim yellow")
            
            if len(search_errors) > 5:
                console.print(f"  ... and {len(search_errors) - 5} more errors", style="dim yellow")
        
        if verbose:
            console.print(f"✅ Search completed: {result.total_matches} matches in {result.files_with_matches} files", style="green")
    
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Search operation failed: {str(e)}")