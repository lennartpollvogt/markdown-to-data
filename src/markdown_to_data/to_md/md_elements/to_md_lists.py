from typing import Dict, Any, Text, List

def _get_task_marker(task: str | None) -> str:
    """Get the appropriate task list marker."""
    if task == 'checked':
        return '[x]'
    elif task == 'unchecked':
        return '[ ]'
    return ''

def _get_list_marker(list_type: str, index: int = 1) -> str:
    """Get the appropriate list marker based on list type."""
    return f"{index}. " if list_type == 'ol' else "- "

def _process_list_items(items: List[Dict[str, Any]], list_type: str, indent_level: int = 0) -> List[str]:
    """
    Process list items recursively and return formatted strings.

    Args:
        items: List of item dictionaries containing content and nested items
        list_type: Type of list ('ul' or 'ol')
        indent_level: Current indentation level

    Returns:
        List of formatted markdown strings
    """
    result = []

    for index, item in enumerate(items, 1):
        # Calculate indentation
        indent = "    " * indent_level

        # Get list marker and task marker
        list_marker = _get_list_marker(list_type, index)
        #task_marker = _get_task_marker(item.get('task'))
        task_marker = _get_task_marker(item['task'])

        # Add space only when there's a task marker
        spacer = " " if task_marker else ""
        line = f"{indent}{list_marker}{task_marker}{spacer}{item['content']}"
        result.append(line)

        # Process nested items if they exist
        if item['items']:
            nested_results = _process_list_items(
                items=item['items'],
                list_type=list_type,  # maintain same list type for nested items
                indent_level=indent_level + 1
            )
            result.extend(nested_results)

    return result

def list_data_to_md(data: Dict[str, Any]) -> Text:
    """
    Convert list data to markdown format.

    Args:
        data: Dictionary containing list data with type and items

    Returns:
        Formatted markdown string

    Example input:
    {
        'list': {
            'type': 'ul',
            'items': [
                {'content': 'item 1', 'items': [], 'task': None},
                {
                    'content': 'item 2',
                    'items': [
                        {'content': 'item 2.1', 'items': [], 'task': None}
                    ],
                    'task': 'checked'
                }
            ]
        }
    }
    """
    # Verify input structure
    if not isinstance(data, dict) or 'list' not in data:
        return ''

    list_data = data['list']
    if not isinstance(list_data, dict) or 'type' not in list_data or 'items' not in list_data:
        return ''

    # Process list items
    formatted_lines = _process_list_items(
        items=list_data['items'],
        list_type=list_data['type']
    )

    # Join all lines with newlines
    return '\n'.join(formatted_lines)
