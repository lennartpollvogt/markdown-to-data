"""
Utility functions for calculating and managing line ranges during markdown processing.

These functions help preserve line number information when merging classified markdown
elements into structured objects.
"""

from typing import List, Dict, Any, Tuple


def calculate_line_range(elements: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Calculate start_line and end_line from a list of classified elements.

    Args:
        elements: List of classified markdown elements, each potentially containing a 'line' field

    Returns:
        Tuple of (start_line, end_line). Returns (0, 0) if no line information is found.
    """
    line_numbers = [elem.get('line', 0) for elem in elements if 'line' in elem and elem['line'] > 0]
    if not line_numbers:
        return 0, 0
    return min(line_numbers), max(line_numbers)


def add_line_range_to_element(element: Dict[str, Any], start_line: int, end_line: int) -> Dict[str, Any]:
    """
    Add start_line and end_line fields to a markdown element.

    Args:
        element: Dictionary representing a markdown element
        start_line: Starting line number
        end_line: Ending line number

    Returns:
        The same element with start_line and end_line fields added
    """
    element['start_line'] = start_line
    element['end_line'] = end_line
    return element


def get_line_from_element(element: Dict[str, Any]) -> int:
    """
    Extract line number from a single classified element.

    Args:
        element: Dictionary representing a classified markdown element

    Returns:
        Line number if found, 0 otherwise
    """
    return element.get('line', 0)


def merge_line_ranges(*ranges: Tuple[int, int]) -> Tuple[int, int]:
    """
    Merge multiple line ranges into a single range.

    Args:
        *ranges: Variable number of (start_line, end_line) tuples

    Returns:
        Tuple of (min_start_line, max_end_line). Returns (0, 0) if no valid ranges.
    """
    valid_ranges = [(start, end) for start, end in ranges if start > 0 and end > 0]
    if not valid_ranges:
        return 0, 0

    min_start = min(start for start, end in valid_ranges)
    max_end = max(end for start, end in valid_ranges)
    return min_start, max_end


def calculate_single_element_range(element: Dict[str, Any]) -> Tuple[int, int]:
    """
    Calculate line range for a single element (start_line = end_line).

    Args:
        element: Dictionary representing a classified markdown element

    Returns:
        Tuple of (line, line) for single-line elements, (0, 0) if no line info
    """
    line = get_line_from_element(element)
    return line, line


def preserve_line_info_in_conversion(source_element: Dict[str, Any], target_element: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transfer line information from a source element to a target element during conversion.

    Args:
        source_element: Original classified element with line information
        target_element: New element to receive line information

    Returns:
        Target element with line information added
    """
    start_line, end_line = calculate_single_element_range(source_element)
    return add_line_range_to_element(target_element, start_line, end_line)
