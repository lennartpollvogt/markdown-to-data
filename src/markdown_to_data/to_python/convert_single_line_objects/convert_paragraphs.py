from typing import List, Dict, Any
from ..merging_multiline_objects.line_utils import preserve_line_info_in_conversion

def _is_paragraph(item: Dict[str, Any]) -> bool:
    """Check if an item is a paragraph."""
    return 'p' in item

def convert_paragraphs(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process classified markdown items, converting paragraphs (p)
    into paragraph objects while maintaining all other markdown elements in their original position.

    Args:
        classified_list: List of classified markdown items

    Returns:
        List containing converted paragraph objects and all other markdown elements
        in their original order
    """
    result = []

    for item in classified_list:
        if _is_paragraph(item):
            # Convert p to paragraph
            paragraph_element = {
                'paragraph': item['p']
            }
            result.append(preserve_line_info_in_conversion(item, paragraph_element))
        else:
            # Keep non-paragraph items as they are
            result.append(item)

    return result
