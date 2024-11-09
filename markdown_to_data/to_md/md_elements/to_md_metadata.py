from typing import Dict, Any, Text, List, Union

def format_metadata_value(value: Any) -> str:
    """Format different types of metadata values."""
    if isinstance(value, (int, float, bool)):
        return str(value)
    elif isinstance(value, list):
        if all(isinstance(x, (int, float)) for x in value):
            # For lists of numbers
            return str(value)
        elif all(isinstance(x, str) for x in value):
            # For lists of strings, keep original format
            if len(value) == 1:
                return f"['{value[0]}']"
            return str(value)
        # For mixed types
        return str(value)
    elif isinstance(value, str):
        if value.startswith('http'):
            return value  # Don't quote URLs
        return value
    return str(value)

def metadata_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert metadata dictionary to markdown format."""
    if not data:
        return ''

    result = ['---']

    # Preserve original order instead of sorting
    for key, value in data.items():
        formatted_value = format_metadata_value(value)
        result.append(f'{key}: {formatted_value}')

    result.append('---')
    return '\n'.join(result)
