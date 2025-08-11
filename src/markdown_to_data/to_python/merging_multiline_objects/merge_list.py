"""
This module handles the merging of classified markdown list items into structured list objects.
It supports unordered lists (ul) and ordered lists (ol), maintaining their hierarchy
and task list properties.
"""
# TODO: be more senstivie to indents in lists

from typing import List, Dict, Any, Tuple
from .line_utils import calculate_line_range, add_line_range_to_element

def _get_list_type(item: Dict[str, Any]) -> str:
    """Determine the type of list item (ul or ol)."""
    return 'ul' if 'ul' in item else 'ol' if 'ol' in item else None

def _create_list_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Create a structured list item from classified markdown item."""
    list_type = _get_list_type(item)
    if list_type is not None:
        li_content = item[list_type]['li']

        # Extract content from various possible keys (p, h1, h2, etc.)
        # The li_content is a dict with content key (p, h1-h6, etc.) and possibly 'indent'
        content = None
        for key, value in li_content.items():
            if key != 'indent':  # Skip the indent key
                content = value
                break

        if content is None:
            content = ''  # Default to empty string if no content found
    else:
        raise Exception

    return {
        'content': content,
        'items': [],
        'task': item[list_type]['task']
    }

def _build_nested_list(items: List[Dict[str, Any]], start_idx: int, base_indent: int) -> Tuple[List[Dict[str, Any]], int]:
    """Build a nested list structure starting from given index."""
    result = []
    i = start_idx

    while i < len(items):
        current_item = items[i]
        current_indent = current_item['marker_indent']

        # If we're back to a lower indent level, exit this nesting level
        if current_indent < base_indent:
            break

        # Create new item
        new_item = _create_list_item(current_item)

        # Look ahead for nested items
        if i + 1 < len(items):
            next_indent = items[i + 1].get('marker_indent', 0)
            if next_indent > current_indent:
                nested_items, new_i = _build_nested_list(items, i + 1, next_indent)
                new_item['items'] = nested_items
                i = new_i - 1

        result.append(new_item)
        i += 1

    return result, i

def _identify_list_segments(classified_md: List[Dict[str, Any]]) -> List[Tuple[List[Dict[str, Any]], str]]:
    """
    Identify continuous list segments.

    Returns:
        List of tuples: (list_items, list_type)
    """
    segments = []
    current_segment = []
    current_type = None
    i = 0

    while i < len(classified_md):
        item = classified_md[i]
        list_type = _get_list_type(item)

        # If it's a list item
        if list_type is not None:
            # Start new segment if needed
            if not current_segment:
                current_type = list_type
                current_segment.append(item)
            # Continue current segment if same type
            elif list_type == current_type:
                current_segment.append(item)
            # End segment if different list type
            else:
                if current_segment:
                    segments.append((current_segment, current_type))
                current_segment = [item]
                current_type = list_type
        # If it's not a list item
        else:
            # If we have a current segment, end it
            if current_segment:
                segments.append((current_segment, current_type))
                current_segment = []
                current_type = None

        i += 1

    # Handle last segment
    if current_segment:
        segments.append((current_segment, current_type))

    return segments

def merge_lists(classified_md: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, merging consecutive list items into structured list objects
    while maintaining all other markdown elements in their original position.

    Args:
        classified_md: List of classified markdown items

    Returns:
        List containing merged list objects and all other markdown elements in their original order
    """
    result = []
    current_segment = []
    current_type = None

    for item in classified_md:
        list_type = _get_list_type(item)

        # If it's a list item
        if list_type is not None:
            # Start new segment if needed
            if not current_segment:
                current_type = list_type
                current_segment.append(item)
            # Continue current segment if same type
            elif list_type == current_type:
                current_segment.append(item)
            # End segment if different list type
            else:
                # Process previous segment
                if current_segment:
                    start_line, end_line = calculate_line_range(current_segment)
                    list_element = {
                        'list': {
                            'type': current_type,
                            'items': _build_nested_list(current_segment, 0, 0)[0]
                        }
                    }
                    add_line_range_to_element(list_element, start_line, end_line)
                    result.append(list_element)
                # Start new segment
                current_segment = [item]
                current_type = list_type

        # If it's not a list item
        else:
            # Process any existing segment
            if current_segment:
                start_line, end_line = calculate_line_range(current_segment)
                list_element = {
                    'list': {
                        'type': current_type,
                        'items': _build_nested_list(current_segment, 0, 0)[0]
                    }
                }
                add_line_range_to_element(list_element, start_line, end_line)
                result.append(list_element)
                current_segment = []
                current_type = None
            # Add non-list item to result
            result.append(item)

    # Handle last segment if exists
    if current_segment:
        start_line, end_line = calculate_line_range(current_segment)
        list_element = {
            'list': {
                'type': current_type,
                'items': _build_nested_list(current_segment, 0, 0)[0]
            }
        }
        add_line_range_to_element(list_element, start_line, end_line)
        result.append(list_element)

    return result
