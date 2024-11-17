from typing import Dict, Any, Text

def header_data_to_md(data: Dict[str, Any]) -> Text:
    """
    Convert header data to markdown format.

    Args:
        data: Dictionary with header level (h1-h6) as key and content as value

    Returns:
        Formatted markdown header string
    """
    if not isinstance(data, dict) or not data:
        return ''

    # Valid header levels
    header_levels = {'h1': '#', 'h2': '##', 'h3': '###',
                    'h4': '####', 'h5': '#####', 'h6': '######'}

    # Get the first (and should be only) key-value pair
    for level, content in data.items():
        if level in header_levels:
            return f"{header_levels[level]} {str(content)}"
        else:
            return content
    return ''
