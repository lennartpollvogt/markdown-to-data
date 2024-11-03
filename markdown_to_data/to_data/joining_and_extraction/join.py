'''
This file contains methods to join the related lines of the classisification outcome.
After joining the lines they get converted into the intended structure of each building block.
'''


from typing import Text, Any, List, Dict

from .extraction import MarkdownExtractor

extractor = MarkdownExtractor()

################
# JOIN RELATED LINES
################

# METADATA
def join_metadata_lines_properly(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Join metadata lines properly and convert them into a dictionary."""
    metadata_dict = {}
    metadata_indices = []

    for i, item in enumerate(classified_list):
        if 'metadata' in item:
            metadata_indices.append(i)
            # Check if metadata is already a dictionary
            if isinstance(item['metadata'], dict):
                metadata_dict.update(item['metadata'])
                continue

            if isinstance(item['metadata'], str) and item['metadata'].strip() == '---':
                continue

            key, value = extractor._extract_metadata_kv(item['metadata'])
            if key:
                metadata_dict[key] = value

    if metadata_dict and metadata_indices:
        # Remove all individual metadata lines
        for index in sorted(metadata_indices, reverse=True):
            classified_list.pop(index)

        # Add the combined metadata dictionary at the start
        classified_list.insert(0, {'metadata': metadata_dict})

    return classified_list

# CODE
def join_code_lines_properly(classified_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
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
                    result.append({'code': extractor._extract_md_code(markdown_snippet='\n'.join(temp_code_block))})
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
        result.append({'code': extractor._extract_md_code(markdown_snippet='\n'.join(temp_code_block))})


    return result

# LISTS
def join_list_lines_properly(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Iterates over each line and joins comprehensive list lines to one list dictionary.
    '''
    result = []
    in_list_block = False
    temp_list_block = []

    for item in classified_list:
        if list(item.keys())[0] == 'list':
            if in_list_block:
                temp_list_block.append(item['list'])
            else:
                in_list_block = True
                temp_list_block.append(item['list'])
        else:
            if in_list_block:
                #result.append({'list': '\n'.join(temp_list_block)})
                result.append({'list': extractor._extract_md_list(markdown_snippet='\n'.join(temp_list_block))})
                temp_list_block.clear()
                in_list_block = False
            result.append(item)

    # Handle any remaining list block
    if in_list_block:
        #result.append({'list': '\n'.join(temp_list_block)})
        result.append({'list': extractor._extract_md_list(markdown_snippet='\n'.join(temp_list_block))})

    return result

# DEFINITION LISTS
def join_def_list_lines_properly(classified_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
    result = []
    current_term = None
    current_definitions = []

    for item in classified_list:
        if list(item.keys())[0] == 'term':
            if current_term:
                # Process the previous definition list
                result.append({
                    'def_list': {
                        'term': current_term,
                        'list': current_definitions
                    }
                })

            # Start a new definition list
            current_term = item['term']
            current_definitions = []
        elif list(item.keys())[0] == 'def_list':
            # Add definition to the current list
            current_definitions.append(item['def_list'].lstrip(': ').strip())
        else:
            # Process the previous definition list if it exists
            if current_term:
                result.append({
                    'def_list': {
                        'term': current_term,
                        'list': current_definitions
                    }
                })
                current_term = None
                current_definitions = []

            # Add non-definition list items to the result
            result.append(item)

    # Process the last definition list if it exists
    if current_term:
        result.append({
            'def_list': {
                'term': current_term,
                'list': current_definitions
            }
        })

    return result

# TABLES
def join_table_lines_properly(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Iterates over each line and joins comprehensive lines with key 'table'.
    Handles various cases including separated tables and tables with multiple column rows.
    '''
    result = []
    in_table_block = False
    temp_table_block = []

    def is_separator_row(row: str) -> bool:
        '''Check if a row is a separator row (contains only '-' between '|')'''
        cells = row.split('|')[1:-1]  # Ignore first and last '|' characters
        return all(cell.strip().replace('-', '') == '' for cell in cells)

    for item in classified_list:
        if list(item.keys())[0] == 'table':
            if in_table_block:
                if is_separator_row(item['table']) and len(temp_table_block) > 1:
                    # take last row
                    last_row = temp_table_block[-1]
                    temp_table_block.pop(-1)
                    # New table detected, finish the previous one
                    #result.append({'table': '\n'.join(temp_table_block)})
                    result.append({'table': extractor._extract_md_table(markdown_snippet='\n'.join(temp_table_block))})
                    temp_table_block = [last_row]
                temp_table_block.append(item['table'])
            else:
                in_table_block = True
                temp_table_block.append(item['table'])
        else:
            if in_table_block:
                if temp_table_block:
                    #result.append({'table': '\n'.join(temp_table_block)})
                    result.append({'table': extractor._extract_md_table(markdown_snippet='\n'.join(temp_table_block))})
                temp_table_block.clear()
                in_table_block = False
            result.append(item)

    # Handle any remaining table block
    if in_table_block and temp_table_block:
        #result.append({'table': '\n'.join(temp_table_block)})
        result.append({'table': extractor._extract_md_table(markdown_snippet='\n'.join(temp_table_block))})

    return result

# BLOCKQUOTES
def join_blockquote_lines_properly(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Joins the comprehensive blockquotes.
    Example:
    [
        {'paragraph': ''},
        {'paragraph': 'some text'},
        {'blockquote': '> Blockquote'},
        {'blockquote': '>> Indent blockquote'},
        {'paragraph': ''},
        {'blockquote': '> new blockquote'}
    ]

    Output:
    [
        {'paragraph': ''},
        {'paragraph': 'some text'},
        {'blockquote': '> Blockquote\n>> Indent blockquote'},
        {'paragraph': ''},
        {'blockquote': '> new blockquote'}
    ]
    '''
    result = []
    in_blockquote = False
    temp_blockquote_content = []

    for item in classified_list:
        if list(item.keys())[0] == 'blockquote':
            if not in_blockquote:
                in_blockquote = True
            temp_blockquote_content.append(item['blockquote'])
        else:
            if in_blockquote:
                #result.append({'blockquote': '\n'.join(temp_blockquote_content)})
                result.append({'blockquote': extractor._extract_md_blockquote(markdown_text='\n'.join(temp_blockquote_content))})
                temp_blockquote_content = []
                in_blockquote = False
            result.append(item)

    # Handle the case where the list ends with a blockquote
    if in_blockquote:
        #result.append({'blockquote': '\n'.join(temp_blockquote_content)})
        result.append({'blockquote': extractor._extract_md_blockquote(markdown_text='\n'.join(temp_blockquote_content))})

    return result

from typing import List, Dict, Any

def delete_empty_paragraphs(classified_list: List[Dict[str, str]]) -> List[Dict[str, str | Any]]:
    '''
    Deletes all rows with key 'paragraph' which are empty (= '').
    '''
    return [item for item in classified_list if not (list(item.keys())[0] == 'paragraph' and list(item.values())[0].strip() == '')]
