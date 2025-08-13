from typing import Dict, List, Any, Text

def transpose_table_data(data: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """
    Transform column-based table data to row-based format.

    Args:
        data: Dictionary with columns as keys and value lists

    Returns:
        List of dictionaries, each representing a row
    """
    if not data:
        return []

    # Get number of rows from length of any column
    num_rows = len(next(iter(data.values())))

    # Create list of row dictionaries
    rows = []
    for i in range(num_rows):
        row = {}
        for col_name, col_values in data.items():
            row[col_name] = col_values[i] if i < len(col_values) else None
        rows.append(row)

    return rows

def calculate_column_widths(
    headers: List[str],
    rows: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Calculate required width for each column.
    """
    widths = {header: len(str(header)) for header in headers}

    for row in rows:
        for header in headers:
            value = str(row.get(header, ''))
            widths[header] = max(widths[header], len(value))

    # Add padding
    return {k: v + 2 for k, v in widths.items()}

def format_row(
    row: Dict[str, Any],
    headers: List[str],
    widths: Dict[str, int]
) -> str:
    """Format a single table row."""
    cells = []
    for header in headers:
        value = str(row.get(header, ''))
        padding = widths[header] - len(value)
        cells.append(f" {value}{' ' * (padding - 1)}")
    return f"|{'|'.join(cells)}|"

def create_separator(headers: List[str], widths: Dict[str, int]) -> str:
    """Create separator row."""
    return '|' + '|'.join('-' * width for width in widths.values()) + '|'

def table_data_to_md(data: Dict[str, Any]) -> Text:
    """
    Convert table data to markdown table format.

    Args:
        data: Dictionary containing table data in column format

    Returns:
        Formatted markdown table string
    """
    if not isinstance(data, dict) or 'table' not in data:
        return ''

    table_data = data['table']
    if not table_data:
        return ''

    # Get headers (column names)
    headers = list(table_data.keys())

    # Transform to row-based format
    rows = transpose_table_data(table_data)
    if not rows:
        return ''

    # Calculate column widths
    widths = calculate_column_widths(headers, rows)

    # Create header row
    header_row = format_row(dict(zip(headers, headers)), headers, widths)

    # Create separator row
    separator_row = create_separator(headers, widths)

    # Create data rows
    data_rows = [format_row(row, headers, widths) for row in rows]

    # Combine all parts with newlines
    table_parts = [header_row, separator_row] + data_rows
    return '\n'.join(table_parts)
