from typing import Dict, Any, Text, List, Union

def process_list_items(items: List[Union[str, Dict]], list_type: str, indent_level: int = 0) -> List[str]:
    """Process list items recursively and return formatted strings."""
    result = []
    for index, item in enumerate(items, 1):
        indent = "  " * indent_level
        marker = f"{index}." if list_type == 'ol' else "-"

        if isinstance(item, dict):
            # Get the parent item text (key) and its children (value)
            parent_text = next(iter(item))  # Get the only key
            children = item[parent_text]    # Get its value (list of children)

            # Add the parent item
            result.append(f"{indent}{marker} {parent_text}")

            # Recursively process children
            nested_results = process_list_items(
                children,
                list_type,
                indent_level + 1
            )
            result.extend(nested_results)
        else:
            # Handle simple string items
            result.append(f"{indent}{marker} {item}")

    return result

def list_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert list data to markdown format."""
    if 'list' not in data or 'type' not in data:
        return ''

    list_type = data['type']  # 'ul' or 'ol'
    items = data['list']

    if not isinstance(items, list):
        return ''

    result = process_list_items(items, list_type)
    return '\n'.join(result)
