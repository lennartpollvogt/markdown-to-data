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
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a h1 header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'separator': '---'},
    {'p': '', 'indent': 0},
    {'h2': 'Header level 2', 'indent': 0},
    {'p': '', 'indent': 0},
    {'p': 'A paragraph after a separator', 'indent': 0},
    {'p': '', 'indent': 0}
]

"""

from typing import List, Dict, Any
from ..merging_multiline_objects.line_utils import preserve_line_info_in_conversion

def _is_separator(item: Dict[str, Any]) -> bool:
    """Check if an item is a separator."""
    return 'hr' in item

def convert_separators(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, converting horizontal rule markers (hr)
    into separator objects while maintaining all other markdown elements in their original position.

    Args:
        classified_list: List of classified markdown items

    Returns:
        List containing converted separator objects and all other markdown elements
        in their original order
    """
    result = []

    for item in classified_list:
        if _is_separator(item):
            # Convert hr to separator
            separator_element = {
                'separator': item['hr']
            }
            result.append(preserve_line_info_in_conversion(item, separator_element))
        else:
            # Keep non-separator items as they are
            result.append(item)

    return result
