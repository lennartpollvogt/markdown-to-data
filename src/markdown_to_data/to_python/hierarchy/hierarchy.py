from typing import List, Dict, Any
from collections import defaultdict


def build_hierarchy_for_dict(merged_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a hierarchical dictionary structure from merged markdown elements.

    The function creates a nested dictionary based on header levels, where headers become keys
    and their content becomes nested dictionaries. Other elements are placed under the most
    recent header. Multiple elements of the same type are automatically numbered (key1, key2, etc).

    Args:
        merged_elements: List of dictionaries containing processed markdown elements

    Returns:
        A nested dictionary representing the hierarchical structure of the markdown document.
        Metadata is placed at the root level if present.

    Example:
        For markdown like:
        ```
        # Header 1
        Some text
        ## Header 2
        - List item
        ```
        Returns:
        {
            "Header 1": {
                "paragraph": "Some text",
                "Header 2": {
                    "list": {
                        "items": ["List item"]
                    }
                }
            }
        }
    """
    # TODO: detect if headers are named equal! -> Exception or warning?
    result: Dict[str, Any] = {}
    current_level = result
    level_stack = [result]
    key_counts = defaultdict(int)

    for item in merged_elements:
        if 'metadata' in item:
            result['metadata'] = item['metadata']
        elif 'header' in item:
            heading_level = item['header']['level']
            heading_text = item['header']['content']

            while len(level_stack) > heading_level:
                level_stack.pop()

            if len(level_stack) < heading_level:
                new_level = {}
                level_stack[-1][heading_text] = new_level
                level_stack.append(new_level)
            else:
                level_stack[-1][heading_text] = {}
                level_stack.append(level_stack[-1][heading_text])

            current_level = level_stack[-1]
            key_counts.clear()  # Reset key counts for each new heading level
        else:
            for key, value in item.items():
                key_counts[key] += 1
                if key_counts[key] > 1:
                    new_key = f"{key}_{key_counts[key]}"
                else:
                    new_key = f"{key}_1"
                    #new_key = key
                current_level[new_key] = value

    return result
