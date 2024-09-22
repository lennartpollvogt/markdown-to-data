from typing import Text, Any, List, Dict
import re

def reset_metdata(current_list: List[Dict[str, Text]]) -> List[Dict[str, Text]]:
    index: int = -1

    for m_dict in current_list:
        index += 1
        print(m_dict)
        if isinstance(m_dict, dict):
            for key, value in m_dict.items():
                if key == 'metadata':
                    if value.strip() == '---':
                        current_list[index] = {'separator': value}
                    else:
                        current_list[index] = {'paragraph': value} 
                # No need for an else clause here
        else:
            print(f"Warning: Unexpected type at index {index}: {type(m_dict)}")

    return current_list