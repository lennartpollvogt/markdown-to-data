"""
An classification of the content of following classified lines:
    - li
    - blockquote

What can be classified:
    - headers
    - paragraphs



Example input:
[
    {
        'ul': {
            'li': 'item',
            'marker': '-',
            'task': None
        },
        'item_indent': 2,
        'marker_indent': 0
    },
    {
        'ul': {
            'li': '# header',
            'marker': '-',
            'task': None
        },
        'item_indent': 2,
        'marker_indent': 0
    },
]

Output:
[
    {
        'ul': {
            'li': {'p': 'item', 'indent': 0},
            'marker': '-',
            'task': None
        },
        'item_indent': 2,
        'marker_indent': 0
    },
    {
        'ul': {
            'li': {
                'h1': 'header',
                'indent': 0
            },
            'marker': '-',
            'task': None
        },
        'item_indent': 2,
        'marker_indent': 0
    },
]

"""
from typing import List, Dict, Any

from .md_classification.classify_md_header import is_header_or_paragraph
from .md_classification.classify_md_paragraph import is_paragraph

def classify_line_content(classified_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classify the content of list items and blockquotes.

    Args:
        classified_lines (List[Dict[str, Any]]): List of classified markdown lines

    Returns:
        List[Dict[str, Any]]: List with classified content in list items and blockquotes
    """
    result = []

    for line_dict in classified_lines:
        # Process unordered lists
        if 'ul' in line_dict:
            content = line_dict['ul']['li']
            processed_content = _process_content(content, indent=0)
            new_dict = dict(line_dict)
            new_dict['ul']['li'] = processed_content
            result.append(new_dict)

        # Process ordered lists
        elif 'ol' in line_dict:
            content = line_dict['ol']['li']
            processed_content = _process_content(content, indent=0)
            new_dict = dict(line_dict)
            new_dict['ol']['li'] = processed_content
            result.append(new_dict)

        # Process blockquotes
        elif 'blockquote' in line_dict:
            content = line_dict['blockquote']
            processed_content = _process_content(content, indent=0)
            new_dict = dict(line_dict)
            new_dict['blockquote'] = processed_content
            result.append(new_dict)

        # Keep other elements unchanged
        else:
            result.append(line_dict)

    return result

def _process_content(content: str, indent: int) -> Dict[str, Any]:
    """
    Process the content of a line to classify it as header or paragraph.

    Args:
        content (str): Content to be classified
        indent (int): Indentation level

    Returns:
        Dict[str, Any]: Classified content as header or paragraph
    """
    stripped_content = content.strip()

    # Check if content is a header
    if stripped_content.startswith('#'):
        return is_header_or_paragraph(
            stripped_line=stripped_content,
            line=content,
            indent=indent
        )

    # Default to paragraph if not a header
    return is_paragraph(content, indent)
