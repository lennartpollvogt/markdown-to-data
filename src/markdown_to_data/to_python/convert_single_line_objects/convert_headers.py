"""
Input:
[
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a h1 header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'hr': '---', 'indent': 0},
    {'p': '', 'indent': 0},
    {'h2': 'Header level 2', 'indent': 0},
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a separator', 'indent': 0},
    {'p': '', 'indent': 0}
]

Output:
[
    {
        'header': {
            'level': 1,
            'content': 'Header'
        }
    },
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a h1 header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'hr': '---', 'indent': 0},
    {'p': '', 'indent': 0},
    {
        'header': {
            'level': 2,
            'content': 'Header level 2'
        }
    },
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a separator', 'indent': 0},
    {'p': '', 'indent': 0}
]
"""
from typing import List, Dict, Any
from ..merging_multiline_objects.line_utils import preserve_line_info_in_conversion

def _is_header(item: Dict[str, Any]) -> bool:
    """Check if an item is a header."""
    return any(f'h{i}' in item for i in range(1, 7))

def _get_header_level(item: Dict[str, Any]) -> int:
    """Get the level of the header (1-6)."""
    for i in range(1, 7):
        if f'h{i}' in item:
            return i
    return 0  # Should never happen if _is_header was called first

def convert_headers(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, converting header markers (h1-h6)
    into structured header objects while maintaining all other markdown elements
    in their original position.

    Args:
        classified_list: List of classified markdown items

    Returns:
        List containing converted header objects and all other markdown elements
        in their original order
    """
    result = []

    for item in classified_list:
        if _is_header(item):
            level = _get_header_level(item)
            content = item[f'h{level}']
            header_element = {
                'header': {
                    'level': level,
                    'content': content
                }
            }
            result.append(preserve_line_info_in_conversion(item, header_element))
        else:
            result.append(item)

    return result
