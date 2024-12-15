from typing import List, Dict, Any

def set_line_keys_to_code(current_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Takes the current final list where we have two entries with key 'code'.
    All keys of the lines between the two 'code' entries are set to 'code'.
    Starting from the last entry of the list which has key 'code', it iterates backwards over each line,
    sets keys to 'code' and stops until it reaches a key which has already 'code' as key.
    '''
    # Find indices of entries containing 'code' key
    code_indices = [i for i, item in enumerate(current_list) if 'code' in item]

    if len(code_indices) < 2:
        return current_list  # Less than two 'code' entries found

    end_index = code_indices[-1]  # Last 'code' entry
    start_index = code_indices[-2]  # Second to last 'code' entry

    # Iterate backwards from the last 'code' entry
    for i in range(end_index - 1, start_index, -1):
        if 'code' not in current_list[i]:
            # Get the text content and indentation if they exist
            content = next(iter(current_list[i].values()))  # Get the first value
            indent = current_list[i].get('indent', 0)  # Get indent if it exists, default to 0

            # Create new dictionary with 'code' key
            current_list[i] = {'code': content, 'indent': indent}

    return current_list
