"""
Tree command implementation for markdown-to-data CLI tool.

This module provides the 'tree' command for displaying markdown structure
as a visual tree representation.
"""

import click
from typing import Optional, Dict, Any
from pathlib import Path

from markdown_to_data import Markdown
from ..utils.constants import COMMAND_DESCRIPTIONS, DEFAULT_MAX_TREE_DEPTH
from ..utils.error_utils import CLIError, validate_markdown_file
from ..utils.file_utils import read_markdown_file, write_text_file, write_json_file
from ..utils.format_utils import create_structure_tree, console, print_json_output


def create_tree_data(md_list, max_depth: Optional[int] = None) -> Dict[str, Any]:
    """
    Create structured tree data from markdown elements.
    
    Args:
        md_list: List of markdown elements
        max_depth: Maximum depth to include
        
    Returns:
        Structured tree data
    """
    tree_data = {
        'type': 'document',
        'children': []
    }
    
    current_depth = 0
    header_stack = [tree_data]  # Stack to track header hierarchy
    
    for element in md_list:
        if max_depth is not None and current_depth >= max_depth:
            break
            
        element_type = next(iter(element))
        element_data = element[element_type]
        
        if element_type == 'metadata':
            metadata_node = {
                'type': 'metadata',
                'data': element_data
            }
            tree_data['children'].append(metadata_node)
        
        elif element_type == 'header':
            level = element_data['level']
            content = element_data['content']
            
            # Determine the correct parent based on header level
            while len(header_stack) > level:
                header_stack.pop()
            
            parent = header_stack[-1]
            header_node = {
                'type': 'header',
                'level': level,
                'content': content,
                'children': []
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(header_node)
            header_stack.append(header_node)
        
        elif element_type == 'list':
            parent = header_stack[-1]
            list_node = {
                'type': 'list',
                'list_type': element_data.get('type', 'ul'),
                'items': element_data.get('items', [])
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(list_node)
        
        elif element_type == 'table':
            parent = header_stack[-1]
            columns = list(element_data.keys())
            row_count = len(element_data[columns[0]]) if columns else 0
            
            table_node = {
                'type': 'table',
                'columns': len(columns),
                'rows': row_count,
                'data': element_data
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(table_node)
        
        elif element_type == 'code':
            parent = header_stack[-1]
            code_node = {
                'type': 'code',
                'language': element_data.get('language', 'text'),
                'lines': len(element_data.get('content', '').split('\n')),
                'content': element_data.get('content', '') if element_type == 'code' else None
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(code_node)
        
        elif element_type == 'blockquote':
            parent = header_stack[-1]
            quote_count = len(element_data) if isinstance(element_data, list) else 1
            
            blockquote_node = {
                'type': 'blockquote',
                'blocks': quote_count,
                'data': element_data
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(blockquote_node)
        
        elif element_type == 'paragraph':
            parent = header_stack[-1]
            content_preview = element_data[:50] + "..." if len(element_data) > 50 else element_data
            
            paragraph_node = {
                'type': 'paragraph',
                'preview': content_preview,
                'content': element_data
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(paragraph_node)
        
        else:
            parent = header_stack[-1]
            other_node = {
                'type': element_type,
                'data': element_data
            }
            
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(other_node)
    
    return tree_data


@click.command('tree')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--max-depth', type=int, default=DEFAULT_MAX_TREE_DEPTH, help='Maximum depth for tree display')
@click.option('--format', '-f', default='tree', 
              type=click.Choice(['tree', 'json']), help='Output format (tree, json)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (optional)')
@click.option('--show-content', is_flag=True, help='Show content previews in tree')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def tree(ctx: click.Context, input_file: str, max_depth: int, format: str, output: Optional[str],
         show_content: bool, verbose: bool) -> None:
    """Display markdown structure as a tree.
    
    This command analyzes a markdown file and displays its structure as a visual
    tree, showing the hierarchy of headers, lists, tables, code blocks, and other elements.
    
    Examples:
        m2d tree document.md
        m2d tree document.md --max-depth 3
        m2d tree document.md --format json --output structure.json
        m2d tree document.md --show-content
    """
    try:
        if verbose:
            console.print(f"🌳 Analyzing structure of: {input_file}", style="dim")
        
        # Validate input file
        validate_markdown_file(input_file)
        
        # Read and parse markdown
        content = read_markdown_file(input_file)
        md = Markdown(content)
        
        if format == 'json':
            # Create structured tree data
            tree_data = create_tree_data(md.md_list, max_depth)
            
            if output:
                write_json_file(output, tree_data)
                if not ctx.obj.get('quiet', False):
                    console.print(f"✅ Tree structure saved to: {output}", style="green")
            else:
                if not ctx.obj.get('quiet', False):
                    print_json_output(tree_data)
        
        else:  # tree format
            # Create visual tree
            tree = create_structure_tree(md.md_list, max_depth)
            
            if output:
                # Save tree as text
                with console.capture() as capture:
                    console.print(tree)
                tree_text = capture.get()
                write_text_file(output, tree_text)
                
                if not ctx.obj.get('quiet', False):
                    console.print(f"✅ Tree visualization saved to: {output}", style="green")
            else:
                if not ctx.obj.get('quiet', False):
                    console.print(tree)
        
        if verbose:
            element_count = len(md.md_list)
            console.print(f"📊 Analyzed {element_count} markdown elements", style="dim")
            
    except CLIError:
        raise
    except Exception as e:
        raise CLIError(f"Failed to create tree structure for '{input_file}': {str(e)}")