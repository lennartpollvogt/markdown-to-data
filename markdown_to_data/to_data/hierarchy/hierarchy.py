from typing import List, Dict, Any
from collections import defaultdict


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
