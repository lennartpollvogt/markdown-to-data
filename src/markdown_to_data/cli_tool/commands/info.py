"""
Info command implementations for markdown-to-data CLI tool.

This module provides the 'info' and 'batch-info' commands for extracting
metadata and structural information from markdown files.
"""

import click
from typing import Optional

from ..utils.constants import COMMAND_DESCRIPTIONS
from ..utils.error_utils import CLIError


@click.command('info')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', default='json', help='Output format (json, table)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def info(ctx: click.Context, input_file: str, output: Optional[str], format: str, verbose: bool) -> None:
    """Extract metadata and structural information from a markdown file."""
    # TODO: Implement in Phase 2
    raise NotImplementedError("The 'info' command will be implemented in Phase 2")


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