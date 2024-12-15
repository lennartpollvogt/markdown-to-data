"""
```markdown
Term of definition list
: item of definition list
: second item of definition list
    A second term of a second definition list
: Item of second def list
  : Item of second def list
```


Output:
[
    {
        'dt': 'Term of definition list',
        'indent': 0
    },
    {
        'dd': 'item of definition list',
        'indent': 0
    },
    {
        'dd': 'second item of definition list',
        'indent': 0
    },
    {
        'dt': 'A second term of a second definition list',
        'indent': 4
    },
    {
        'dd': 'Item of second def list',
        'indent': 0
    },
    {
        'dd': 'Item of second def list',
        'indent': 2
    }
]
"""

from typing import Dict, Any, Tuple, List, Optional

def is_definition_list_item(line: str, previous_dict: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a line is part of a definition list and format it accordingly.

    Args:
        line (str): Current line to check
        previous_dict (Optional[Dict[str, Any]]): Dictionary containing the previous line's classification

    Returns:
        Tuple[bool, Dict[str, Any]]: (is_definition_list, formatted_dict)
    """
    stripped_line = line.strip()
    indent = len(line) - len(line.lstrip())

    # If line doesn't start with ': ', it might be a term
    if not stripped_line.startswith(': '):
        return False, {}

    # No previous line available
    if previous_dict is None:
        return False, {}

    # Get previous line's key and value
    previous_key = list(previous_dict.keys())[0]
    previous_value = previous_dict[previous_key]

    # Cases for previous line
    if previous_key == 'p':
        # Previous line is a paragraph that could be a term
        if previous_value.strip() and not previous_value.startswith(':'):
            # Convert previous paragraph to definition term
            return True, {
                'convert_previous': {
                    'dt': previous_value,
                    'indent': previous_dict.get('indent', 0)
                },
                'current': {
                    'dd': stripped_line[2:],  # Remove ': ' prefix
                    'indent': indent
                }
            }
        # Empty paragraph or starts with ':'
        return False, {'p': line, 'indent': indent}

    elif previous_key == 'dd':
        # Continue existing definition list
        return True, {
            'dd': stripped_line[2:],
            'indent': indent
        }

    # Any other case, treat as regular paragraph
    return False, {'p': line, 'indent': indent}

def process_definition_list(lines: List[str], start_idx: int) -> Tuple[List[Dict[str, Any]], int]:
    """
    Process a section of definition list.

    Args:
        lines (List[str]): All lines of the document
        start_idx (int): Starting index for processing

    Returns:
        Tuple[List[Dict[str, Any]], int]: (processed_items, last_index)
    """
    processed_items: List[Dict[str, Any]] = []
    current_idx = start_idx

    # Process the first line as a potential term
    if current_idx < len(lines):
        first_line = lines[current_idx]
        first_line_indent = len(first_line) - len(first_line.lstrip())
        processed_items.append({
            'dt': first_line.strip(),
            'indent': first_line_indent
        })
        current_idx += 1

    while current_idx < len(lines):
        line = lines[current_idx]
        stripped_line = line.strip()

        # If line doesn't start with ': ', we've found a new term
        if not stripped_line.startswith(': '):
            if not stripped_line:  # Empty line
                break
            # New term
            indent = len(line) - len(line.lstrip())
            processed_items.append({
                'dt': stripped_line,
                'indent': indent
            })
            current_idx += 1
            continue

        # Process description
        indent = len(line) - len(line.lstrip())
        processed_items.append({
            'dd': stripped_line[2:].strip(),  # Remove ': ' prefix
            'indent': indent
        })
        current_idx += 1

    return processed_items, current_idx - 1
