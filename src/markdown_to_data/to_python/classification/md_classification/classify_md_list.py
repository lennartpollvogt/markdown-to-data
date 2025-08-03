import re
from typing import Tuple

def is_unordered_list_item(stripped_line: str, line: str) -> Tuple[bool, str, str, str | None, int, int]:
    """
    Check if line is an unordered list item and return value, marker, task status, indent and marker_indent.

    Args:
        stripped_line (str): Line with whitespace stripped
        line (str): Original line

    Returns:
        Tuple[bool, str, str, str | None, int, int]:
            - is_list: Whether line is a valid list item
            - content: Content after marker/checkbox (stripped)
            - marker: List marker used
            - task_status: 'checked', 'unchecked', or None for regular lists
            - item_indent: Total indentation to content
            - marker_indent: Indentation before marker
    """
    markers = {'-', '*', '+'}

    # Get the initial indent before the marker
    marker_indent = len(line) - len(line.lstrip())
    non_stripped_line = line.lstrip()

    # Check if remaining line starts with a marker
    if not any(non_stripped_line.startswith(m) for m in markers):
        return False, '', '', None, 0, 0

    marker = non_stripped_line[0]

    # Must have at least one space after marker
    if len(non_stripped_line) < 2 or non_stripped_line[1] != ' ':
        return False, '', '', None, 0, 0

    # Check for task list format
    remaining_content = non_stripped_line[2:].lstrip()
    task_match = re.match(r'^\[([ xX])\](\s*)(.*)$', remaining_content)

    if task_match:
        status = 'checked' if task_match.group(1).lower() == 'x' else 'unchecked'
        spaces_after_checkbox = task_match.group(2)
        content = task_match.group(3).rstrip()

        # Base indentation for task list (marker + space + [ + x/space + ])
        base_indent = marker_indent + 5

        # Add additional spaces if there's content
        if content:
            item_indent = base_indent + len(spaces_after_checkbox)
        else:
            item_indent = base_indent

        return True, content, marker, status, item_indent, marker_indent

    # Regular unordered list item
    content = remaining_content.rstrip()

    # Check if it's not a separator
    if all(c == marker or c.isspace() for c in content):
        marker_count = sum(1 for c in content if c == marker)
        if marker_count >= 2:
            return False, '', '', None, 0, 0

    spaces_after_marker = len(non_stripped_line[2:]) - len(remaining_content)
    item_indent = marker_indent + 2  # marker + space
    if content:
        item_indent += spaces_after_marker

    return True, content, marker, None, item_indent, marker_indent

def is_ordered_list_item(stripped_line: str, line: str) -> Tuple[bool, str, str, str | None, int, int]:
    """
    Check if line is an ordered list item and return value, marker, task status, indent and marker_indent.

    Args:
        stripped_line (str): Line with whitespace stripped
        line (str): Original line

    Returns:
        Tuple[bool, str, str, str | None, int, int]:
            - is_list: Whether line is a valid list item
            - content: Content after marker/checkbox (stripped)
            - marker: List marker used
            - task_status: 'checked', 'unchecked', or None for regular lists
            - item_indent: Total indentation to content
            - marker_indent: Indentation before marker
    """
    marker_indent = len(line) - len(line.lstrip())
    non_stripped_line = line.lstrip()

    # Check for ordered list format
    list_match = re.match(r'^(\d{1,9}[).])(\s+)(.+)$', non_stripped_line)
    if not list_match:
        return False, '', '', None, 0, 0

    marker = list_match.group(1)
    spaces_after_marker = list_match.group(2)
    remaining_content = list_match.group(3)

    # Check for task list format
    task_match = re.match(r'^\[([ xX])\](\s*)(.*)$', remaining_content)

    if task_match:
        status = 'checked' if task_match.group(1).lower() == 'x' else 'unchecked'
        spaces_after_checkbox = task_match.group(2)
        content = task_match.group(3).rstrip()

        # Base indentation (marker + space + [ + x/space + ])
        base_indent = marker_indent + 6

        # Add additional spaces if there's content
        if content:
            item_indent = base_indent + len(spaces_after_checkbox)
        else:
            item_indent = base_indent

        return True, content, marker, status, item_indent, marker_indent

    # Regular ordered list item
    content = remaining_content.rstrip()
    item_indent = marker_indent + len(marker)
    if content:
        item_indent += len(spaces_after_marker)

    return True, content, marker, None, item_indent, marker_indent
