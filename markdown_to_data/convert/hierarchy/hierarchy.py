from typing import List, Dict, Any
from collections import defaultdict

def build_hierarchy_for_list(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a hierarchical list of sections based on headings from a flat list.

    Args:
    classified_list (List[Dict[str, Any]]): The flat list of classified markdown elements

    Returns:
    List[Dict[str, Any]]: A list of sections representing the markdown structure
    """
    result = []
    stack = [result]
    current_level = 0

    for item in classified_list:
        for i in range(1, 7):  # Handle h1 to h6
            if f'h{i}' in item:
                while current_level >= i:
                    stack.pop()
                    current_level -= 1
                new_section = {f'h{i}': {'title': item[f'h{i}'], 'content': []}}
                stack[-1].append(new_section)
                stack.append(new_section[f'h{i}']['content'])
                current_level = i
                break
        else:
            if 'metadata' in item:
                stack[-1].append(item)
            else:
                stack[-1].append(item)

    return result



def build_hierarchy_for_dict(classified_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_level = result
    level_stack = [result]
    key_counts = defaultdict(int)

    for item in classified_list:
        if 'metadata' in item:
            result['metadata'] = item['metadata']
        elif any(key.startswith('h') for key in item.keys()):
            heading_level = int(next(key for key in item.keys() if key.startswith('h'))[1])
            heading_text = next(iter(item.values()))

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
                    new_key = f"{key}{key_counts[key]}"
                else:
                    new_key = key
                current_level[new_key] = value

    return result
