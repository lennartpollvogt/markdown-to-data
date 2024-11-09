from typing import Dict, Any, Text

def count_nesting_level(item: Any) -> int:
    """Count the number of nested blockquotes."""
    level = 0
    current = item
    while isinstance(current, list):
        level += 1
        if not current:  # Handle empty list
            break
        current = current[0]
    return level

def blockquote_data_to_md(data: Dict[str, Any]) -> Text:
    if 'blockquote' not in data:
        return ''

    result = []
    for line in data['blockquote']:
        level = count_nesting_level(line)
        # Get the actual text value by accessing the innermost list
        current = line
        while isinstance(current, list):
            if not current:  # Handle empty list
                current = ''
                break
            current = current[0]

        # Add '>' characters based on nesting level
        prefix = '>' * level
        result.append(f'{prefix} {current}')

    return '\n'.join(result)
