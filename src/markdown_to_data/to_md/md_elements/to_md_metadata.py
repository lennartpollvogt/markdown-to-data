from typing import Dict, Any, Text, List, Union

def format_metadata_value(value: Any) -> str:
    """Format different types of metadata values."""
    if isinstance(value, bool):
        return str(value)  # Will return 'True' or 'False'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        if all(isinstance(x, (int, float)) for x in value):
            return str(value)
        elif all(isinstance(x, str) for x in value):
            # For lists of strings, join without quotes
            return f"[{', '.join(value)}]"
        return str(value)
    elif isinstance(value, str):
        # String that looks like 'true' or 'false' should stay lowercase
        if value.lower() in ('true', 'false'):
            return value.lower()
        # Otherwise return the string as is, without quotes
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
