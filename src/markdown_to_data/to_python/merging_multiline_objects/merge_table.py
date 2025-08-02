"""
This module handles the merging of classified markdown table rows into structured table objects.
It supports tables with and without headers, handling inconsistent columns and missing values.
"""

from typing import List, Dict, Any
from .line_utils import calculate_line_range, add_line_range_to_element

def _is_table_row(item: Dict[str, Any]) -> bool:
    """Check if an item is a table row."""
    return 'tr' in item

def _is_separator(item: Dict[str, Any]) -> bool:
    """Check if an item is a table separator."""
    return _is_table_row(item) and item['tr'] == 'table_separator'

def _normalize_value(value: Any) -> Any:
    """Normalize cell values, converting empty strings to None."""
    if value == '':
        return None
    return value

def _extract_headers(segment: List[Dict[str, Any]]) -> List[str]:
    """Extract headers from table segment or generate column numbers."""
    max_cols = max(
        len(row['tr']) for row in segment
        if _is_table_row(row) and isinstance(row['tr'], dict)
    )

    # Find first row (header candidates)
    header_row = next(
        (row for row in segment if _is_table_row(row) and isinstance(row['tr'], dict)),
        None
    )

    # If there's a separator, use first row as headers
    has_separator = any(_is_separator(row) for row in segment)
    if has_separator and header_row:
        headers = []
        for i in range(1, max_cols + 1):
            key = f'td_{i}'
            header_value = header_row['tr'].get(key)
            headers.append(header_value if header_value else f'col_{i}')
        return headers

    # Generate numbered columns
    return [f'col_{i}' for i in range(1, max_cols + 1)]

def _build_column_structure(segment: List[Dict[str, Any]], headers: List[str]) -> Dict[str, List[Any]]:
    """Build column-based structure from table data."""
    # Initialize columns
    columns = {header: [] for header in headers}

    # Find start of data rows
    start_idx = 0
    has_separator = any(_is_separator(row) for row in segment)
    if has_separator:
        start_idx = 1
        for i, row in enumerate(segment):
            if _is_separator(row):
                start_idx = i + 1
                break

    # Process data rows
    for row in segment[start_idx:]:
        if not _is_table_row(row) or not isinstance(row['tr'], dict):
            continue

        # Add values to each column
        for i, header in enumerate(headers):
            key = f'td_{i+1}'
            value = _normalize_value(row['tr'].get(key))
            columns[header].append(value)

    return columns

def _process_table_segment(segment: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a continuous segment of table rows into a structured table."""
    headers = _extract_headers(segment)
    columns = _build_column_structure(segment, headers)

    # Calculate line range for the table
    start_line, end_line = calculate_line_range(segment)

    table_element = {
        'table': columns
    }
    add_line_range_to_element(table_element, start_line, end_line)

    return table_element

def merge_tables(classified_md: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, merging consecutive table rows into structured table objects
    while maintaining all other markdown elements in their original position.

    Args:
        classified_md: List of classified markdown items

    Returns:
        List containing merged table objects and all other markdown elements in their original order
    """
    result = []
    current_segment = []

    for item in classified_md:
        if _is_table_row(item):
            current_segment.append(item)
        else:
            # Process any existing segment
            if current_segment:
                result.append(_process_table_segment(current_segment))
                current_segment = []
            # Add non-table item to result
            result.append(item)

    # Handle last segment if exists
    if current_segment:
        result.append(_process_table_segment(current_segment))

    return result
