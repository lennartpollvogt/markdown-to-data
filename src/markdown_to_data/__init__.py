"""
markdown_to_data - Convert markdown and its elements (tables, lists, code, etc.) into structured, easily processable data formats like lists and hierarchical dictionaries (or JSON), with support for parsing back to markdown.
"""

from .markdown_to_data import Markdown
from .to_md.to_md_parser import to_md_parser

__all__ = [
    'Markdown',
    'to_md_parser'
]

__version__ = "0.1.0"
