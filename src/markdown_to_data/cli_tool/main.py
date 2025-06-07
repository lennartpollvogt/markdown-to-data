"""
Main CLI entry point for markdown-to-data tool.

This module provides the main command group and sets up the CLI structure
for all markdown-to-data commands.
"""

import sys
from typing import NoReturn


def check_cli_dependencies() -> bool:
    """Check if CLI dependencies are available."""
    try:
        import click
        import rich
        import psutil
        return True
    except ImportError:
        return False


def show_cli_installation_message() -> NoReturn:
    """Show message about installing CLI dependencies."""
    print("❌ CLI dependencies not found!")
    print()
    print("The markdown-to-data CLI tool requires additional dependencies.")
    print("Please install them using one of these commands:")
    print()
    print("  pip install 'markdown-to-data[cli]'")
    print("  uv add 'markdown-to-data[cli]'")
    print("  pip install markdown-to-data click rich psutil")
    print()
    print("After installation, the 'm2d' command will be available.")
    sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    if not check_cli_dependencies():
        show_cli_installation_message()
    
    # Only import CLI modules if dependencies are available
    try:
        import click
        from .commands import info, convert, extract, md, tree, search
        from .utils.error_utils import CLIError, handle_cli_error
    except ImportError as e:
        print(f"❌ Failed to import CLI modules: {e}")
        show_cli_installation_message()
    
    # Set up the actual CLI
    setup_and_run_cli()


def setup_and_run_cli() -> None:
    """Set up and run the actual CLI after dependencies are confirmed."""
    import click
    from .commands import info, convert, extract, md, tree, search
    from .utils.error_utils import CLIError, handle_cli_error


    @click.group(name='m2d')
    @click.version_option(message='%(version)s')
    @click.option(
        '--verbose', '-v',
        is_flag=True,
        help='Enable verbose output'
    )
    @click.option(
        '--quiet', '-q',
        is_flag=True,
        help='Suppress non-error output'
    )
    @click.pass_context
    def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
        """
        markdown-to-data CLI tool

        Convert markdown files to structured data formats and perform various
        operations on markdown content including extraction, analysis, and conversion.

        Use 'm2d COMMAND --help' for detailed help on specific commands.
        """
        # Ensure context object exists
        ctx.ensure_object(dict)

        # Store global options in context
        ctx.obj['verbose'] = verbose
        ctx.obj['quiet'] = quiet

        # Validate conflicting options
        if verbose and quiet:
            raise click.BadParameter("Cannot use both --verbose and --quiet options")

    # Add command groups
    cli.add_command(info.info)
    cli.add_command(info.batch_info)
    cli.add_command(convert.convert)
    cli.add_command(convert.batch_convert)
    cli.add_command(extract.extract)
    cli.add_command(extract.batch_extract)
    cli.add_command(md.md)
    cli.add_command(md.batch_md)
    cli.add_command(tree.tree)
    cli.add_command(search.search)

    # Run the CLI
    try:
        cli()
    except CLIError as e:
        handle_cli_error(e)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
