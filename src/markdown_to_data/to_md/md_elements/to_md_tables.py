'''
Requirements and processing steps:
1. Look in every column for the longest entry (column/header names included). White spaces between words count as well.
2. The number of characters (= n) of the longest entry will be added by 2 more white spaces (= n+2; one for the beginning and one for the end)
    a. Example: 'Column Header' has a length of 13 (including whitespace between). When this is the longest entry in its column, the width of the column will be 15.
    b. Consider: Another column might have short or longer entries, which why it is necessary to get for every column the longest entry.
    c. Consider: A entry start after '| ' (beware whitespace after `|`) with trailing whitespaces to meet the length of the set width of the column
    d. Consider: A column in each row starts and ends with a `|`
3. Start with the header row of the table.
4. Separate the header row from the value rows with '|---|' (number of `-` depends on column width)
5. Add the value rows with their entries.

Example:
'table': [
    {
        'Service': 'Cloud Services',
        'Q1 Sales ($)': '100,000',
        'Q2 Sales ($)': '150,000',
        'Total Sales ($)': '250,000',
        'Growth (%)': '50%'
    },
    {
        'Service': 'Maintenance',
        'Q1 Sales ($)': '80,000',
        'Q2 Sales ($)': '90,000',
        'Total Sales ($)': '170,000',
        'Growth (%)': '12.5%'
    },
    {
        'Service': 'Consulting',
        'Q1 Sales ($)': '50,000',
        'Q2 Sales ($)': '70,000',
        'Total Sales ($)': '120,000',
        'Growth (%)': '40%'
    }
]

In the table the longest entry is 'Total Sales ($)'. It has 15 characters (indluding white spaces).
That means, the width of each column will be 15 + 2 = 17

The table would in fact look like this:
| Service         | Q1 Sales ($)    | Q2 Sales ($)    | Total Sales ($) | Growth (%)      |
|-----------------|-----------------|-----------------|-----------------|-----------------|
| Cloud Services  | 100,000         | 150,000         | 250,000         | 50%             |
| Maintenance     | 80,000          | 90,000          | 170,000         | 12.5%           |
| Consulting      | 50,000          | 70,000          | 120,000         | 40%             |

'''
from typing import Dict, List, Any, Text, Union

def calculate_column_widths(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate the required width for each column based on the longest entry.

    Args:
        data: List of dictionaries representing table rows

    Returns:
        Dictionary mapping column names to their required widths
    """
    if not data:
        return {}

    widths = {}
    headers = data[0].keys()

    for header in headers:
        # Start with header length
        max_length = len(str(header))
        # Check each row's value length
        for row in data:
            value_length = len(str(row[header]))
            max_length = max(max_length, value_length)
        # Add 2 for padding (one space on each side)
        widths[header] = max_length + 2

    return widths

def format_row(row: Dict[str, Any], widths: Dict[str, int]) -> str:
    """
    Format a single row according to the calculated column widths.

    Args:
        row: Dictionary representing a single table row
        widths: Dictionary of column widths

    Returns:
        Formatted row string with proper padding and separators
    """
    formatted_cells = []

    for column, width in widths.items():
        value = str(row[column])
        # Calculate padding needed after the value
        padding = width - len(value) - 1  # -1 because we add one space at start
        formatted_cell = f" {value}{' ' * padding}"
        formatted_cells.append(formatted_cell)

    return f"|{'|'.join(formatted_cells)}|"

def create_separator(widths: Dict[str, int]) -> str:
    """
    Create the separator row between header and data.

    Args:
        widths: Dictionary of column widths

    Returns:
        Separator row string with proper width
    """
    separators = []

    for width in widths.values():
        separators.append('-' * width)

    return f"|{'|'.join(separators)}|"

def table_data_to_md(data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]) -> Text:
    """
    Convert table data to markdown table format.

    Args:
        data: Either a list of dictionaries representing table rows,
              or a dictionary with a 'table' key containing the list

    Returns:
        Formatted markdown table string
    """
    # Handle both direct list input and dictionary with 'table' key
    if isinstance(data, dict):
        if 'table' not in data:
            return ''
        table_data = data['table']
    else:
        table_data = data

    # Validate input
    if not table_data or not isinstance(table_data, list):
        return ''

    # Calculate column widths
    widths = calculate_column_widths(table_data)

    # Create header row using first row's keys
    headers = {header: header for header in table_data[0].keys()}
    header_row = format_row(headers, widths)

    # Create separator row
    separator_row = create_separator(widths)

    # Create data rows
    data_rows = [format_row(row, widths) for row in table_data]

    # Combine all parts
    return '\n'.join([header_row, separator_row] + data_rows)
