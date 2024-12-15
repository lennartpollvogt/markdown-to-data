from typing import Dict, Any, Tuple

def is_blockquote(line: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Create a blockquote dictionary entry.

    Counts the '>' markers (including those without whitespaces after the first).

    Args:
        line (str): The line to check for blockquote formatting

    Returns:
        Tuple[bool, Dict[str, Any]]:
            - Boolean indicating if line is a blockquote
            - Dictionary with blockquote content and level if is blockquote,
              empty dict otherwise
    """
    stripped_line = line.lstrip()

    # Check if line starts with '>'
    if not stripped_line.startswith('>'):
        return False, {}

    # Count consecutive '>' markers
    level = 0
    content_start = 0

    for i, char in enumerate(stripped_line):
        if char == '>':
            level += 1
            content_start = i + 1
        elif char.isspace():
            continue
        else:
            break

    # Extract content after markers
    content = stripped_line[content_start:].lstrip()

    return True, {'blockquote': content, 'level': level}
