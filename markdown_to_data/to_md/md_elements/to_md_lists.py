from typing import Dict, Any, Text, List, Tuple

def process_list_items(items: List[Any], list_type: str, indent_level: int = 0) -> List[str]:
    """Process list items recursively and return formatted strings."""
    result = []
    for index, item in enumerate(items, 1):
        # Handle the main item
        indent = "  " * indent_level
        marker = f"{index}." if list_type == 'ol' else "-"

        if isinstance(item, list):
            main_text = item[0]
            # Add the main item
            result.append(f"{indent}{marker} {main_text}")

            # Handle nested lists if they exist
            if len(item) > 1 and isinstance(item[1], list):
                nested_items = item[1]
                # Recursively process nested items
                nested_results = process_list_items(
                    nested_items,
                    list_type,
                    indent_level + 1
                )
                result.extend(nested_results)
        else:
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
