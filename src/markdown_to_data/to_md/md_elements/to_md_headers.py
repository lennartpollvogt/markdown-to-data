from typing import Dict, Any, Text, TypedDict

class HeaderContent(TypedDict):
    level: int
    content: str

class HeaderData(TypedDict):
    header: HeaderContent

def get_header_level_type(level: int) -> str:
    """Convert numeric header level to type string."""
    return f'h{level}'

def header_data_to_md(data: Dict[str, Any] | None) -> Text:
    """
    Convert header data to markdown format.

    Args:
        data: Dictionary containing header data with 'level' and 'content'
        Expected structure:
        {
            'header': {
                'level': int (1-6),
                'content': str
            }
        }

    Returns:
        Formatted markdown header string

    Examples:
        >>> header_data_to_md({'header': {'level': 1, 'content': 'Title'}})
        '# Title\\n'
        >>> header_data_to_md({'header': {'level': 2, 'content': 'Subtitle'}})
        '## Subtitle\\n'
    """
    # Basic validation
    if not isinstance(data, dict) or 'header' not in data:
        return ''

    header_data = data['header']

    # Validate header structure
    if not isinstance(header_data, dict) or \
       'level' not in header_data or \
       'content' not in header_data:
        return ''

    # Get level and content
    level = header_data['level']
    content = header_data['content']

    # Validate level
    if not isinstance(level, int) or level < 1 or level > 6:
        return ''

    # Convert level to markdown header syntax
    header_marks = '#' * level

    # Format header with content
    # Ensure content is converted to string and stripped of leading/trailing whitespace
    return f"{header_marks} {str(content).strip()}"
