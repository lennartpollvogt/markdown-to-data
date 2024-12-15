from typing import Dict, Any, Text, List, TypedDict

class BlockquoteItem(TypedDict):
    content: str
    items: List['BlockquoteItem']

def process_blockquote_item(item: BlockquoteItem, level: int = 1) -> List[str]:
    """
    Process a blockquote item and its nested items recursively.

    Args:
        item: Dictionary containing 'content' and 'items' fields
        level: Current nesting level (default: 1)

    Returns:
        List of properly formatted markdown lines
    """
    result = []
    prefix = '>' * level + ' '

    # Add the current item's content
    result.append(f"{prefix}{item['content']}")

    # Process nested items if any
    for nested_item in item['items']:
        result.extend(process_blockquote_item(nested_item, level + 1))

    return result

def blockquote_data_to_md(data: Dict[str, Any]) -> Text:
    """
    Convert blockquote data structure to markdown format.

    Args:
        data: Dictionary containing blockquote data

    Returns:
        Formatted markdown string
    """
    if 'blockquote' not in data:
        return ''

    result = []
    for item in data['blockquote']:
        result.extend(process_blockquote_item(item))

    return '\n'.join(result) + '\n'
