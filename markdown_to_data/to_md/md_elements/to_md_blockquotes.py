from typing import Dict, Any, Text, Union, List

def process_blockquote_item(item: Union[str, Dict], level: int = 1) -> List[str]:
    """
    Process a blockquote item and its nested content recursively.
    Returns a list of properly formatted markdown lines.
    """
    result = []
    prefix = '>' * level + ' '

    if isinstance(item, dict):
        # Get the parent text and its children
        parent_text = next(iter(item))  # Get the only key
        children = item[parent_text]    # Get its value (nested content)

        # Add the parent line
        result.append(f"{prefix}{parent_text}")

        # Process children based on their type
        if isinstance(children, list):
            # Process list of items
            for child in children:
                result.extend(process_blockquote_item(child, level + 1))
        elif isinstance(children, dict):
            # Process nested dictionary
            result.extend(process_blockquote_item(children, level + 1))
    else:
        # Handle simple string items
        result.append(f"{prefix}{item}")

    return result

def blockquote_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert blockquote data structure to markdown format."""
    if 'blockquote' not in data:
        return ''

    result = []
    for item in data['blockquote']:
        result.extend(process_blockquote_item(item))

    return '\n'.join(result)
