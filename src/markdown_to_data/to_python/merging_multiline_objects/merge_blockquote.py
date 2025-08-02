"""
Example:

input:
[
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'blockquote': {'p': 'a single line blockquote', 'indent': 0}, 'level': 1},
    {'p': '', 'indent': 0},
    {'blockquote': {'p': 'a nested blockquote', 'indent': 0}, 'level': 1},
    {'blockquote': {'p': 'with multiline', 'indent': 0}, 'level': 1},
    {'blockquote': {'p': 'the nested part', 'indent': 0}, 'level': 2},
    {'blockquote': {'p': 'last line of the blockquote', 'indent': 0}, 'level': 1}
]

output:
[
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {
        'blockquote': [
            {
                'content': 'a single line blockquote',
                'items': []
            }
        ]
    },
    {'p': '', 'indent': 0},
    {
        'blockquote': [
            {
                'content': 'a nested blockquote',
                'items': []
            },
            {
                'content': 'with multiline'',
                'items': [
                    {
                        'content': 'the nested part',
                        'items': []
                    }
                ]
            },
            {
                'content': 'last line of the blockquote',
                'items': []
            }
        ]
    }
]
"""

from typing import List, Dict, Any, Tuple
from .line_utils import calculate_line_range, add_line_range_to_element

def _is_blockquote(item: Dict[str, Any]) -> bool:
    """Check if an item is a blockquote."""
    return 'blockquote' in item

def _get_blockquote_content(item: Dict[str, Any]) -> str:
    """
    Extract content from a blockquote item.

    Handles two possible blockquote structures:
    1. Simple format: {'blockquote': 'text content'}
    2. Detailed format: {'blockquote': {'p': 'text content'}}

    This flexibility is needed because blockquotes can be classified in different
    formats depending on their context and complexity in the markdown document.

    Args:
        item: Dictionary containing a blockquote entry

    Returns:
        The text content of the blockquote

    Example:
        >>> _get_blockquote_content({'blockquote': 'simple text'})
        'simple text'
        >>> _get_blockquote_content({'blockquote': {'p': 'detailed text'}})
        'detailed text'
        """
    if isinstance(item['blockquote'], dict):
        return item['blockquote']['p']
    return item['blockquote']

def _build_nested_blockquote(items: List[Dict[str, Any]], start_idx: int, base_level: int) -> Tuple[List[Dict[str, Any]], int]:
    """Build a nested blockquote structure starting from given index."""
    result = []
    i = start_idx

    while i < len(items):
        current_item = items[i]

        if not _is_blockquote(current_item) or current_item['level'] < base_level:
            break

        current_level = current_item['level']

        # Create new blockquote item
        new_item = {
            'content': _get_blockquote_content(current_item),
            'items': []
        }

        # Handle nesting
        if current_level > base_level:
            # This is a nested item, add to previous item's items
            if not result:
                # Should never happen with valid input
                raise ValueError("Invalid blockquote structure")

            nested_items, new_i = _build_nested_blockquote(items, i, current_level)
            result[-1]['items'].extend(nested_items)
            i = new_i
        else:
            # This is an item at the current level
            result.append(new_item)
            i += 1

    return result, i

def merge_blockquotes(classified_md: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, merging consecutive blockquotes into structured objects
    while maintaining all other markdown elements in their original position.

    Args:
        classified_md: List of classified markdown items

    Returns:
        List containing merged blockquote objects and all other markdown elements
        in their original order
    """
    result = []
    i = 0

    while i < len(classified_md):
        current_item = classified_md[i]

        if _is_blockquote(current_item):
            # Start of a blockquote segment
            base_level = current_item['level']
            blockquote_items, new_i = _build_nested_blockquote(classified_md, i, base_level)

            # Calculate line range for blockquote segment
            blockquote_segment = classified_md[i:new_i]
            start_line, end_line = calculate_line_range(blockquote_segment)

            # Add merged blockquote structure
            blockquote_element = {
                'blockquote': blockquote_items
            }
            add_line_range_to_element(blockquote_element, start_line, end_line)
            result.append(blockquote_element)

            i = new_i
        else:
            # Add non-blockquote items directly
            result.append(current_item)
            i += 1

    return result
