"""
MD command implementations for markdown-to-data CLI tool.

This module provides the 'md' and 'batch-md' commands for converting
JSON data back to markdown format.
"""

import click
from typing import Optional, List

from ..utils.constants import COMMAND_DESCRIPTIONS, SUPPORTED_ELEMENT_TYPES
from ..utils.error_utils import CLIError


@click.command('md')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output markdown file path')
@click.option('--include', multiple=True, help=f'Element types to include. Supported: {", ".join(SUPPORTED_ELEMENT_TYPES)}')
@click.option('--exclude', multiple=True, help=f'Element types to exclude. Supported: {", ".join(SUPPORTED_ELEMENT_TYPES)}')
@click.option('--spacer', type=int, default=1, help='Number of empty lines between elements')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def md(ctx: click.Context, input_file: str, output: Optional[str], include: tuple, exclude: tuple,
       spacer: int, overwrite: bool, verbose: bool) -> None:
    """Convert JSON data back to markdown format."""
    # TODO: Implement in Phase 3
    raise NotImplementedError("The 'md' command will be implemented in Phase 3")


@click.command('batch-md')
@click.argument('pattern', default='**/*.json')
@click.option('--output-dir', type=click.Path(), help='Output directory for markdown files')
@click.option('--include', multiple=True, help=f'Element types to include. Supported: {", ".join(SUPPORTED_ELEMENT_TYPES)}')
@click.option('--exclude', multiple=True, help=f'Element types to exclude. Supported: {", ".join(SUPPORTED_ELEMENT_TYPES)}')
@click.option('--spacer', type=int, default=1, help='Number of empty lines between elements')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def batch_md(ctx: click.Context, pattern: str, output_dir: Optional[str], include: tuple, exclude: tuple,
             spacer: int, recursive: bool, overwrite: bool, verbose: bool) -> None:
    """Convert multiple JSON files back to markdown format."""
    # TODO: Implement in Phase 4
    raise NotImplementedError("The 'batch-md' command will be implemented in Phase 4")