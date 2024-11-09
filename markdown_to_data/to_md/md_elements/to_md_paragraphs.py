from typing import Dict, Any, Text, Union

def paragraph_data_to_md(data: Union[Dict[str, Any], str]) -> Text:
    """Convert paragraph data to markdown format."""
    # Handle direct string input
    if isinstance(data, str):
        return data

    # Handle dictionary input
    if isinstance(data, dict) and 'paragraph' in data:
        return str(data['paragraph'])

    return ''
