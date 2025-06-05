"""
Convert command implementations for markdown-to-data CLI tool.

This module provides the 'convert' and 'batch-convert' commands for converting
markdown files to JSON format.
"""

import click
from typing import Optional
from pathlib import Path

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
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_convert(ctx: click.Context, pattern: str, output_dir: Optional[str], format: str,
                 indent: int, compact: bool, recursive: bool, overwrite: bool, verbose: bool) -> None:
    """Convert multiple markdown files to JSON format."""
    # TODO: Implement in Phase 4
    raise NotImplementedError("The 'batch-convert' command will be implemented in Phase 4")