from typing import Text, Any, List, Dict
import re


def reset_metdata(current_list: List[Dict[str, Text]]) -> List[Dict[str, Text]]:
    index: int = -1

    for m_dict in current_list:
        index += 1
        if isinstance(m_dict, dict):
            for key, value in m_dict.items():
                if key == 'metadata':
                    if value.strip() == '---':
                        current_list[index] = {'separator': value}
                    else:
                        current_list[index] = {'paragraph': value} 
        else:
            print(f"Warning: Unexpected type at index {index}: {type(m_dict)}")

    return current_list

def set_line_keys_to_code(current_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Takes the current final list where we have two entries with key 'code'.
    All keys of the lines between the two 'code' entries are set to 'code'.
    Starting from the last entry of the list which has key 'code', it iterates backwards over each line,
    sets keys to 'code' and stops until it reaches a key which has already 'code' as key.
    '''
    # Find indices of 'code' entries
    code_indices = [i for i, item in enumerate(current_list) if list(item.keys())[0] == 'code']
    
    #if len(code_indices) < 2:
        #return current_list  # Less than two 'code' entries found
    
    end_index = code_indices[-1]  # Last 'code' entry
    start_index = code_indices[-2]  # Second to last 'code' entry
    
    # Iterate backwards from the last 'code' entry
    for i in range(end_index - 1, start_index, -1):
        if list(current_list[i].keys())[0] != 'code':
            current_list[i] = {'code': list(current_list[i].values())[0]}
    
    return current_list

                
def md_line_classification(markdown: Text) -> List[Dict[str, Any]]:
    '''
    This function detects different kind of building blocks from markdown, extracts them and store them into a tuple.
    '''
    markdown = markdown.lstrip() # delete whitespace from beginning
    lines: List[Text] = markdown.splitlines()
    final_list: List[Dict[str, Any]] = []
    # INDEX
    index_of_line: int = -1
    # METADATA
    in_metadata: bool = False
    metadata: bool = False
    # CODE
    in_code: bool = False

    for line in lines:
        stripped_line: Text = line.strip()

        # HEADERS
        if stripped_line.startswith('#'):
            # Check if there's a space after the '#' characters
            match = re.match(r'^(#+)\s+(.*)', stripped_line)
            if match:
                # Extract the level and the header text
                level = len(match.group(1))
                header_text = match.group(2)
                
                # Ensure the level doesn't exceed 6 (maximum header level in Markdown)
                level = min(level, 6)
                line = {f'h{level}': header_text}
                final_list.append(line)
                index_of_line += 1
            else:
                # If there's no space, treat it as a paragraph
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1

        # LISTS
        elif stripped_line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.', stripped_line):
            line = {'list': line}
            final_list.append(line)
            index_of_line += 1

        # DEFINITION LISTS
        elif stripped_line.startswith(": "):
            previous_line: int = index_of_line # TODO: make a function out of it
            previous_dict: dict = final_list[previous_line]
            previous_key: List[Text] = list(previous_dict.keys())
            previous_value: List[Text] = list(previous_dict.values())

            if previous_key[0] == 'paragraph' and previous_value[0].strip() != '' and not previous_value[0].startswith(':'):
                previous_dict = {'term': previous_value[0]}
                final_list[previous_line] = previous_dict
                line = {'def_list': line}
                final_list.append(line)
                index_of_line += 1
            elif previous_key[0] == 'paragraph' and previous_value[0].strip() == '':
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1
            elif previous_key[0] == 'def_list':
                line = {'def_list': line}
                final_list.append(line)
                index_of_line += 1
            else:
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1

        # TABLES
        elif stripped_line.startswith('|') and '|' in line:
            line = {'table': line}
            final_list.append(line)
            index_of_line += 1

        # BLOCKQUOTES
        elif stripped_line.startswith('>'):
            line = {'blockquote': line}
            final_list.append(line)
            index_of_line += 1

        # CODE
        elif stripped_line.startswith('```'):
            if in_code is False:
                line = {'code': line}
                final_list.append(line)
                in_code = True
                index_of_line += 1
            elif in_code is True:
                line = {'code': line}
                final_list.append(line)
                # TODO: search from the last line reverse the next line with code in final_list. All lines in between get key 'code'
                final_list = set_line_keys_to_code(current_list=final_list)
                in_code = False
                index_of_line += 1

        # METADATA or SEPARATOR
        elif stripped_line.startswith('---'):
            if in_metadata:
                line = {'metadata': line}
                final_list.append(line)
                in_metadata = False
                metadata = True # signal metadata was found and closed
                index_of_line += 1
            else:
                line = {'separator': line}
                final_list.append(line)
                index_of_line += 1

        # METADATA or PARAGRAPH
        elif re.match(r'^[^:\s]+:\s*.*$', stripped_line):
            if in_metadata is True and metadata is False and index_of_line != -1:
                line = {'metadata': line}
                final_list.append(line)
                index_of_line += 1
            elif in_metadata is False and metadata is False and index_of_line != -1: # could the last expression lead to problems?
                previous_line: int = index_of_line - 1
                previous_dict: dict = final_list[previous_line]
                previous_key = list(previous_dict.keys())
                previous_value = list(previous_dict.values())
                if previous_key[0] == 'separator':
                    in_metadata = True
                    previous_dict = {'metadata': previous_value[0]}
                    final_list[previous_line] = previous_dict
                    line = {'metadata': line}
                    final_list.append(line)
                    index_of_line += 1
                else:
                    line = {'paragraph': line}
                    final_list.append(line)
                    index_of_line += 1
            else: # TODO: proof this case can happen?
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1
        else:
            # METADATA
            if in_metadata: # such a case will not make it into the metadata
                if stripped_line.strip() == '':
                    continue # TODO: This causes to have index_of_line += 1 in every if-else statement. Alternative?
                else:

                    in_metadata = False
                    line = {'paragraph': line}
                    final_list.append(line)
                    # set previous lines to correct key
                    final_list = reset_metdata(current_list=final_list)
                    index_of_line += 1
            elif metadata is True:

                line = {'paragraph': line}
                final_list.append(line) #
                index_of_line += 1
            elif stripped_line.strip() == '':
                continue
            else:
                line = {'paragraph': line}
                final_list.append(line) #
                index_of_line += 1

    return final_list