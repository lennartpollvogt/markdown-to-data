from typing import Dict, Any, Text
import re

def _needs_quotes(value: str) -> bool:
    """Determine if a string value needs quotes."""
    special_chars = [':', ',', '#']  # Add more special characters if needed
    return (any(char in value for char in special_chars) and
            not (value.startswith('"') and value.endswith('"')) and
            not (value.startswith("'") and value.endswith("'")))

def _transform_key(key: str) -> str:
    """Transform key from Python format to markdown format."""
    return re.sub(r'_', ' ', key)

def format_metadata_value(value: Any) -> str:
    """Format different types of metadata values."""
    if value is None:
        return ''

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, list):
        if not value:
            return '[]'

        if all(isinstance(x, (int, float)) for x in value):
            return ', '.join(str(x) for x in value)

        if all(isinstance(x, str) for x in value):
            formatted_items = []
            for item in value:
                if _needs_quotes(item):
                    formatted_items.append(f'"{item}"')
                else:
                    formatted_items.append(item)

            if any('"' in item for item in formatted_items):
                return f'[{", ".join(formatted_items)}]'
            return ', '.join(formatted_items)

        return str(value)

    if isinstance(value, str):
        if value.lower() in ('true', 'false'):
            return value.lower()
        if _needs_quotes(value):
            return f'"{value}"'
        return value

    return str(value)

def metadata_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert metadata dictionary to markdown format."""
    if not data:
        return ''

    # Extract the inner metadata dictionary if it exists
    metadata = data.get('metadata', {}) if isinstance(data, dict) else {}

    if not metadata:
        return ''

    result = ['---']

    for key, value in metadata.items():
        transformed_key = _transform_key(key)
        formatted_value = format_metadata_value(value)
        result.append(f'{transformed_key}: {formatted_value}')

    result.append('---')
    return '\n'.join(result)
