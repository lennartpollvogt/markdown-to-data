from typing import List, Dict, Any

def build_hierarchy(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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