from typing import Dict, Any, Text

def definition_list_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert definition list data to markdown format."""
    if 'term' not in data or 'list' not in data:
        return ''

    term = data['term']
    definitions = data['list']

    if not isinstance(definitions, list):
        return ''

    # Format the term and definitions
    result = [term]  # Start with the term
    # Add each definition with the ':' prefix
    result.extend(f": {definition}" for definition in definitions)

    return '\n'.join(result)
