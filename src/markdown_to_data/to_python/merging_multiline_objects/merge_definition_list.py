"""
input:
[
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {'dt': 'term 1', 'indent': 0},
    {'dd': 'definition 1', 'indent': 0},
    {'dd': 'definition 2', 'indent': 0},
    {'p': '', 'indent': 0},
    {'dt': 'term 2', 'indent': 0},
    {'dd': 'definition 1', 'indent': 0},
    {'dd': 'definition 2', 'indent': 0},
    {'p': '', 'indent': 0}
]

output:
[
    {'h1': 'Header', 'indent': 0},
    {'p': '', 'indent': 0},
    {
        'def_list': {
            'term': 'term 1',
            'list': ['definition 1', 'definition 2']
        }
    },
    {'p': '', 'indent': 0},
    {
        'def_list': {
            'term': 'term 2',
            'list': ['definition 1', 'definition 2']
        }
    },
    {'p': '', 'indent': 0}
]
"""

from typing import List, Dict, Any

def _is_definition_term(item: Dict[str, Any]) -> bool:
    """Check if the item is a definition term."""
    return 'dt' in item

def _is_definition_description(item: Dict[str, Any]) -> bool:
    """Check if the item is a definition description."""
    return 'dd' in item

def merge_definition_lists(classified_md: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, merging definition terms and descriptions into structured objects
    while maintaining all other markdown elements in their original position.

    Args:
        classified_md: List of classified markdown items

    Returns:
        List containing merged definition list objects and all other markdown elements
        in their original order
    """
    result = []
    i = 0

    while i < len(classified_md):
        current_item = classified_md[i]

        # If we find a definition term
        if _is_definition_term(current_item):
            term = current_item['dt']
            definitions = []

            # Look ahead for definitions
            j = i + 1
            while j < len(classified_md) and _is_definition_description(classified_md[j]):
                definitions.append(classified_md[j]['dd'])
                j += 1

            # Create definition list object
            def_list = {
                'def_list': {
                    'term': term,
                    'list': definitions
                }
            }
            result.append(def_list)

            # Move index past the processed definitions
            i = j
        else:
            # Add non-definition list items directly to result
            result.append(current_item)
            i += 1

    return result
