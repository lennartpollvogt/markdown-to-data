from typing import List, Dict, Any

# MERGING
from .merging_multiline_objects.merge_list import merge_lists
from .merging_multiline_objects.merge_definition_list import merge_definition_lists
from .merging_multiline_objects.merge_blockquote import merge_blockquotes
from .merging_multiline_objects.merge_metadata import merge_metadata
from .merging_multiline_objects.merge_table import merge_tables
from .merging_multiline_objects.merge_code import merge_code_blocks
# CONVERSION
from .convert_single_line_objects.convert_headers import convert_headers
from .convert_single_line_objects.convert_separators import convert_separators
from .convert_single_line_objects.convert_paragraphs import convert_paragraphs
# HIERARCHY
from .hierarchy.hierarchy import build_hierarchy_for_dict

def merge_classified_markdown_lines(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of classified markdown lines and merges them into meaningful markdown elements.

    This function processes individual classified lines and combines them into structured markdown
    elements like lists, tables, and blockquotes. It handles both multi-line elements that need
    to be merged and single-line elements that need consistent formatting.

    Args:
        classified_list: List of dictionaries containing classified markdown lines

    Returns:
        List of dictionaries containing processed and merged markdown elements

    The function handles these markdown elements:
        - Lists (ordered and unordered)
        - Blockquotes (including nested)
        - Definition lists
        - Tables (with and without headers)
        - Metadata (front matter)
        - Headers (h1-h6)
        - Paragraphs
        - Separators
    """
    merged_elements = []

    # METADATA - Process first to preserve line information
    # Merge metadata
    merged_elements = merge_metadata(classified_list=classified_list)

    # MERGING MULTLINE ELEMENTS TOGETHER
    # Merge lists
    merged_elements = merge_lists(classified_md=merged_elements)
    # Merge definition lists
    merged_elements = merge_definition_lists(classified_md=merged_elements)
    # Merge definition lists
    merged_elements = merge_blockquotes(classified_md=merged_elements)
    # Merge tables
    merged_elements = merge_tables(classified_md=merged_elements)
    # Merge code blocks
    merged_elements = merge_code_blocks(classified_list=merged_elements)

    # CONVERSION TO ALIGN OTHER ELEMENTS TO REQUIRED STRUCTURE
    # Convert headers
    merged_elements = convert_headers(classified_list=merged_elements)
    # Convert paragraphs
    merged_elements = convert_paragraphs(classified_list=merged_elements)
    # Convert separators
    merged_elements = convert_separators(classified_list=merged_elements)

    # EMPTY PARAGRAPHS -> REMOVE
    merged_elements = [
            element for element in merged_elements
            if not (
                'paragraph' in element and
                not element['paragraph'].strip()
            )
        ]

    return merged_elements

def hierarchy_with_merged_markdown_lines(merged_elements: List[Dict[str, Any]]) -> Dict[str, Any]:

    hierarchy_dict = build_hierarchy_for_dict(merged_elements=merged_elements)

    return hierarchy_dict
