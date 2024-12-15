from typing import List, Text, Any, Dict
import re

def _extract_md_code(markdown_snippet: str) -> Dict[str, Any]:
    '''
    Extracts a markdown code block out of the given markdown text snippet.
    The first appearing markdown code block is extracted while others are ignored.
    '''
    lines = markdown_snippet.splitlines()
    in_code_block = False
    code_block_lines = []
    potential_language = None
    code_block_found = False

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('```'):
            if not in_code_block:
                # Start of code block
                in_code_block = True
                code_block_found = True
                # Get potential language identifier
                potential_language = stripped_line[3:].strip()
                continue
            else:
                # End of code block
                break
        if in_code_block:
            code_block_lines.append(line)

    if code_block_found:  # Changed from if code_block_lines
        # Process the content
        # Find common indentation
        non_empty_lines = [line for line in code_block_lines if line.strip()]
        if non_empty_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
            # Remove common indentation
            content = '\n'.join(line[min_indent:] if line.strip() else ''
                                for line in code_block_lines).strip()
        else:
            content = ''

        # Validate language identifier
        if potential_language and re.match(r'^[a-zA-Z0-9+-]+$', potential_language):
            language = potential_language.lower()
        else:
            language = None
            if potential_language:
                content = f"{potential_language}\n{content}"

        return {
            "language": language,
            "content": content
        }

    return {}

# CODE
def merge_code_blocks(classified_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
    '''
    Iterates over the final list and joines the code lines into a single line.
    It checks for starting ``` and ending ``` to join correctly.
    Each joined line gets separated by \n
    '''
    result: List[Dict[str, Text | Any]] = []
    in_code_block = False
    temp_code_block = []
    start_delimiter = None

    for item in classified_list:
        if list(item.keys())[0] == 'code':
            if item['code'].startswith('```'):
                if in_code_block:
                    # End of code block
                    temp_code_block.append(item['code'])
                    #result.append({'code': '\n'.join(temp_code_block)})
                    result.append({'code': _extract_md_code(markdown_snippet='\n'.join(temp_code_block))})
                    temp_code_block.clear()
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    start_delimiter = item['code'].strip()
                    temp_code_block.append(item['code'])
            elif in_code_block:
                temp_code_block.append(item['code'])
        else:
            if in_code_block:
                # If we encounter non-code items while in a code block, treat them as part of the code
                temp_code_block.append(list(item.values())[0])
            else:
                result.append(item)
    # Handle any remaining code block
    if in_code_block:
        temp_code_block.append(start_delimiter)
        #result.append({'code': '\n'.join(temp_code_block)})
        result.append({'code': _extract_md_code(markdown_snippet='\n'.join(temp_code_block))})


    return result
