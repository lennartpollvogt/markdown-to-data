"""
Output formatting utilities for markdown-to-data CLI tool.

This module provides utilities for formatting and displaying output
in various formats including JSON, tree structures, and terminal-friendly displays.
"""

import json
from typing import Dict, Any, List, Optional, Union
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich.columns import Columns
from rich import box

console = Console()


def format_json_output(
    data: Union[Dict[str, Any], List[Dict[str, Any]]], 
    indent: Optional[int] = 2,
    compact: bool = False
) -> str:
    """
    Format data as JSON string with proper indentation.
    
    Args:
        data: Data to format as JSON
        indent: JSON indentation level (None for compact)
        compact: Whether to use compact formatting
        
    Returns:
        Formatted JSON string
    """
    if compact:
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    else:
        return json.dumps(data, indent=indent, ensure_ascii=False)


def print_json_output(
    data: Union[Dict[str, Any], List[Dict[str, Any]]], 
    indent: Optional[int] = 2,
    compact: bool = False,
    highlight: bool = True
) -> None:
    """
    Print data as formatted JSON to console.
    
    Args:
        data: Data to print as JSON
        indent: JSON indentation level
        compact: Whether to use compact formatting
        highlight: Whether to use syntax highlighting
    """
    json_str = format_json_output(data, indent, compact)
    
    if highlight:
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
    else:
        console.print(json_str)


def create_info_table(info_data: Dict[str, Any], title: str = "File Information") -> Table:
    """
    Create a rich table for displaying file information.
    
    Args:
        info_data: Dictionary containing file information
        title: Table title
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    for key, value in info_data.items():
        if isinstance(value, dict):
            # Handle nested dictionaries
            for nested_key, nested_value in value.items():
                display_key = f"{key}.{nested_key}"
                table.add_row(display_key, str(nested_value))
        elif isinstance(value, list):
            # Handle lists
            if value:
                table.add_row(key, ", ".join(str(v) for v in value))
            else:
                table.add_row(key, "[dim]None[/dim]")
        else:
            table.add_row(key, str(value) if value is not None else "[dim]None[/dim]")
    
    return table


def create_metadata_display(metadata: Dict[str, Any]) -> Panel:
    """
    Create a rich panel for displaying metadata information.
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        Rich Panel object
    """
    if not metadata:
        return Panel("[dim]No metadata found[/dim]", title="Metadata", border_style="blue")
    
    content = []
    for key, value in metadata.items():
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value)
        else:
            value_str = str(value)
        
        content.append(f"[cyan]{key}:[/cyan] {value_str}")
    
    return Panel("\n".join(content), title="Metadata", border_style="blue")


def create_structure_tree(md_list: List[Dict[str, Any]], max_depth: Optional[int] = None) -> Tree:
    """
    Create a tree representation of markdown structure.
    
    Args:
        md_list: List of markdown elements
        max_depth: Maximum depth to display (None for unlimited)
        
    Returns:
        Rich Tree object
    """
    tree = Tree("📄 Document Structure")
    current_depth = 0
    header_stack = [tree]  # Stack to track header hierarchy
    
    for i, element in enumerate(md_list):
        if max_depth is not None and current_depth >= max_depth:
            break
            
        element_type = next(iter(element))
        element_data = element[element_type]
        
        if element_type == 'metadata':
            metadata_node = tree.add("📋 Metadata")
            for key, value in element_data.items():
                if isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                metadata_node.add(f"[cyan]{key}:[/cyan] {value_str}")
        
        elif element_type == 'header':
            level = element_data['level']
            content = element_data['content']
            
            # Determine the correct parent based on header level
            while len(header_stack) > level:
                header_stack.pop()
            
            parent = header_stack[-1]
            header_emoji = "📍" if level == 1 else "📌" if level == 2 else "📎"
            header_node = parent.add(f"{header_emoji} H{level}: {content}")
            header_stack.append(header_node)
        
        elif element_type == 'list':
            parent = header_stack[-1]
            list_type = element_data.get('type', 'ul')
            list_emoji = "📝" if list_type == 'ol' else "📋"
            
            list_node = parent.add(f"{list_emoji} List ({list_type.upper()})")
            _add_list_items(list_node, element_data.get('items', []), max_depth=2)
        
        elif element_type == 'table':
            parent = header_stack[-1]
            columns = list(element_data.keys())
            row_count = len(element_data[columns[0]]) if columns else 0
            parent.add(f"📊 Table ({len(columns)} columns, {row_count} rows)")
        
        elif element_type == 'code':
            parent = header_stack[-1]
            language = element_data.get('language', 'text')
            lines = len(element_data.get('content', '').split('\n'))
            parent.add(f"💻 Code Block ({language}, {lines} lines)")
        
        elif element_type == 'blockquote':
            parent = header_stack[-1]
            quote_count = len(element_data) if isinstance(element_data, list) else 1
            parent.add(f"💬 Blockquote ({quote_count} blocks)")
        
        elif element_type == 'def_list':
            parent = header_stack[-1]
            term = element_data.get('term', 'Unknown')
            def_count = len(element_data.get('list', []))
            parent.add(f"📚 Definition List: {term} ({def_count} definitions)")
        
        elif element_type == 'paragraph':
            parent = header_stack[-1]
            content_preview = element_data[:50] + "..." if len(element_data) > 50 else element_data
            parent.add(f"📄 Paragraph: {content_preview}")
        
        else:
            parent = header_stack[-1]
            parent.add(f"❓ {element_type.title()}")
    
    return tree


def _add_list_items(parent_node, items: List[Dict[str, Any]], max_depth: int = 2, current_depth: int = 0):
    """
    Recursively add list items to tree node.
    
    Args:
        parent_node: Parent tree node
        items: List of list items
        max_depth: Maximum nesting depth to show
        current_depth: Current nesting depth
    """
    if current_depth >= max_depth:
        return
    
    for item in items[:5]:  # Limit to first 5 items
        content = item.get('content', '')
        task_status = item.get('task')
        
        if task_status == 'checked':
            icon = "✅"
        elif task_status == 'unchecked':
            icon = "❌"
        else:
            icon = "•"
        
        # Truncate long content
        if len(content) > 40:
            content = content[:37] + "..."
        
        item_node = parent_node.add(f"{icon} {content}")
        
        # Add nested items
        nested_items = item.get('items', [])
        if nested_items and current_depth < max_depth - 1:
            _add_list_items(item_node, nested_items, max_depth, current_depth + 1)
    
    # Show count if there are more items
    if len(items) > 5:
        parent_node.add(f"... and {len(items) - 5} more items")


def create_summary_table(summary_data: Dict[str, Any]) -> Table:
    """
    Create a summary table for batch processing results.
    
    Args:
        summary_data: Summary statistics
        
    Returns:
        Rich Table object
    """
    table = Table(title="Processing Summary", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="white", justify="right")
    table.add_column("Percentage", style="green", justify="right")
    
    total = summary_data.get('total_files', 0)
    processed = summary_data.get('processed', 0)
    successful = summary_data.get('successful', 0)
    failed = summary_data.get('failed', 0)
    
    if total > 0:
        success_rate = (successful / total) * 100
        failure_rate = (failed / total) * 100
    else:
        success_rate = failure_rate = 0
    
    table.add_row("Total Files", str(total), "100.0%")
    table.add_row("Processed", str(processed), f"{(processed/total)*100:.1f}%" if total > 0 else "0%")
    table.add_row("Successful", str(successful), f"{success_rate:.1f}%")
    table.add_row("Failed", str(failed), f"{failure_rate:.1f}%")
    
    return table


def create_error_panel(error_message: str, details: Optional[str] = None) -> Panel:
    """
    Create an error panel for displaying error information.
    
    Args:
        error_message: Main error message
        details: Optional detailed error information
        
    Returns:
        Rich Panel object
    """
    content = [f"[red]{error_message}[/red]"]
    
    if details:
        content.append(f"\n[dim]{details}[/dim]")
    
    return Panel(
        "\n".join(content), 
        title="❌ Error", 
        border_style="red",
        expand=False
    )


def create_warning_panel(warning_message: str) -> Panel:
    """
    Create a warning panel for displaying warning information.
    
    Args:
        warning_message: Warning message
        
    Returns:
        Rich Panel object
    """
    return Panel(
        f"[yellow]{warning_message}[/yellow]", 
        title="⚠️  Warning", 
        border_style="yellow",
        expand=False
    )


def create_success_panel(success_message: str) -> Panel:
    """
    Create a success panel for displaying success information.
    
    Args:
        success_message: Success message
        
    Returns:
        Rich Panel object
    """
    return Panel(
        f"[green]{success_message}[/green]", 
        title="✅ Success", 
        border_style="green",
        expand=False
    )


def format_file_list(files: List[str], title: str = "Files") -> Columns:
    """
    Format a list of files for display.
    
    Args:
        files: List of file paths
        title: Title for the list
        
    Returns:
        Rich Columns object
    """
    if not files:
        return Columns([Text("[dim]No files found[/dim]")])
    
    file_items = []
    for filepath in files:
        # Show relative path if it's shorter
        display_path = filepath
        if len(filepath) > 50:
            display_path = "..." + filepath[-47:]
        
        file_items.append(Text(f"📄 {display_path}"))
    
    return Columns(file_items, expand=True, equal=True)


def print_verbose_info(message: str, verbose: bool = False) -> None:
    """
    Print verbose information if verbose mode is enabled.
    
    Args:
        message: Message to print
        verbose: Whether verbose mode is enabled
    """
    if verbose:
        console.print(f"[dim]ℹ️  {message}[/dim]")


def print_quiet_success(message: str, quiet: bool = False) -> None:
    """
    Print success message unless quiet mode is enabled.
    
    Args:
        message: Success message to print
        quiet: Whether quiet mode is enabled
    """
    if not quiet:
        console.print(f"[green]✅ {message}[/green]")


class ProgressFormatter:
    """Utility class for formatting progress information."""
    
    @staticmethod
    def format_time_remaining(seconds: float) -> str:
        """Format remaining time in human readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_speed(items_per_second: float) -> str:
        """Format processing speed."""
        if items_per_second < 1:
            return f"{items_per_second:.2f} files/s"
        else:
            return f"{items_per_second:.1f} files/s"


def create_element_summary_table(elements_info: Dict[str, Any]) -> Table:
    """
    Create a table showing summary of markdown elements found.
    
    Args:
        elements_info: Dictionary with element counts and information
        
    Returns:
        Rich Table object
    """
    table = Table(title="Markdown Elements Summary", box=box.ROUNDED)
    table.add_column("Element Type", style="cyan")
    table.add_column("Count", style="white", justify="right")
    table.add_column("Variants", style="green")
    table.add_column("Details", style="dim")
    
    element_icons = {
        'metadata': '📋',
        'header': '📍',
        'paragraph': '📄',
        'list': '📝',
        'table': '📊',
        'code': '💻',
        'blockquote': '💬',
        'def_list': '📚',
        'separator': '➖'
    }
    
    for element_type, info in elements_info.items():
        if isinstance(info, dict) and 'count' in info:
            icon = element_icons.get(element_type, '❓')
            count = info['count']
            variants = ', '.join(info.get('variants', []))
            
            # Create details string based on element type
            details = ""
            summary = info.get('summary', {})
            
            if element_type == 'header' and 'levels' in summary:
                levels = summary['levels']
                details = f"Levels: {', '.join(f'H{k}({v})' for k, v in levels.items())}"
            elif element_type == 'list' and 'task_stats' in summary:
                task_stats = summary['task_stats']
                details = f"Tasks: {task_stats.get('checked', 0)}✅ {task_stats.get('unchecked', 0)}❌"
            elif element_type == 'table' and 'total_cells' in summary:
                details = f"Total cells: {summary['total_cells']}"
            elif element_type == 'code' and 'languages' in summary:
                languages = summary['languages']
                details = f"Languages: {', '.join(f'{k}({v})' for k, v in languages.items())}"
            
            table.add_row(
                f"{icon} {element_type.replace('_', ' ').title()}", 
                str(count),
                variants or "[dim]None[/dim]",
                details or "[dim]None[/dim]"
            )
    
    return table