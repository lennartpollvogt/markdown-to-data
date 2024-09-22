markdown_example = '''
---

title: Example
author: John Doe
tags: [python, code]

---
---

title: Example
author: John Doe
tags: [python, code]

---

Just text

# Sample Markdown #Lists

## Lists

### Unordered Lists
- Item 1
- Item 2
    - Subitem 1
        - Subsubitem 1
    - Subitem 2
- Item 3

- Item 1
- Item 2

```Python

def hello_world():
    print('Hello World!)
```
```Python
def hello_world():
    print('Hello World!)
```

### Ordered List
4. First item reversed
3. Second item
    1. Subitem 1
    2. Subitem 2
2. Third item

1. First item
2. Second item

## Not a List

This is just regular text.

Again regular text

## Table
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

| Column 1 | Column 2 |
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

A definition list
: The definition of a list
: The next line of the definition
some text
A definition list
: The definition of a list
: The next line of the definition

some text
> Blockquote
>> Indent blockquote

> new blockquote
'''


from typing import Text, Any, List, Dict
import re
import rich

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

    # join all lines from end_index to start_index
    
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
    in_code: bool = False # TODO: missing

    for line in lines:
        
        stripped_line: Text = line.strip()

        
        # HEADER
        if stripped_line.startswith('#'):
            # Count consecutive '#' characters at the beginning of the line
            level = 0
            for char in stripped_line:
                if char == '#':
                    level += 1
                else:
                    break # TODO: could make problems
            
            # Ensure the level doesn't exceed 6 (maximum header level in Markdown)
            level = min(level, 6)
            line = {f'h{level}': line}
            print(f'found HEADER of level {level}')
            final_list.append(line)
            index_of_line += 1

        # LISTS
        elif stripped_line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.', stripped_line):
            print('found LIST')
            line = {'list': line}
            final_list.append(line)
            index_of_line += 1

        # DEFINITION LISTS
        elif stripped_line.startswith(": "):
            previous_line: int = index_of_line # TODO: make a function out of it
            print(f'INDEX RANGE {previous_line}')
            previous_dict: dict = final_list[previous_line]
            previous_key: List[Text] = list(previous_dict.keys())
            print('previous key: ' + previous_key[0])
            previous_value: List[Text] = list(previous_dict.values())
            print('previous value: ' + previous_value[0])

            if previous_key[0] == 'paragraph' and previous_value[0].strip() != '' and not previous_value[0].startswith(':'):
                print('found DEF LIST')
                print('RESET PREVIOUS PARAGRAPH TO DEF_LIST')
                previous_dict = {'term': previous_value[0]}
                final_list[previous_line] = previous_dict
                line = {'def_list': line}
                final_list.append(line)
                index_of_line += 1
            elif previous_key[0] == 'paragraph' and previous_value[0].strip() == '':
                print('found PARAGRAPH')
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1
            elif previous_key[0] == 'def_list':
                print('extend DEF_LIST')
                line = {'def_list': line}
                final_list.append(line)
                index_of_line += 1
            else:
                print('found PARAGRAPH')
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1



        # TABLES
        elif stripped_line.startswith('|') and '|' in line:
            print('found TABLE')
            line = {'table': line}
            final_list.append(line)
            index_of_line += 1
        # BLOCKQUOTES
        elif stripped_line.startswith('>'):
            print('found BLOCKQUOTE')
            line = {'blockquote': line}
            final_list.append(line)
            index_of_line += 1
        # CODE
        elif stripped_line.startswith('```'):
            if in_code is False:
                print('found CODE')
                line = {'code': line}
                final_list.append(line)
                in_code = True
                index_of_line += 1
            elif in_code is True:
                print('end CODE')
                line = {'code': line}
                final_list.append(line)
                # TODO: search from the last line reverse the next line with code in final_list. All lines in between get key 'code'
                final_list = set_line_keys_to_code(current_list=final_list)
                in_code = False
                index_of_line += 1

        # METADATA or SEPARATOR
        elif stripped_line.startswith('---'):
            if in_metadata:
                print('found METADATA END')
                line = {'metadata': line}
                final_list.append(line)
                in_metadata = False
                metadata = True # signal metadata was found and closed
                index_of_line += 1
            else:
                print('found SEPARATOR')
                line = {'separator': line}
                final_list.append(line)
                index_of_line += 1

        # METADATA or PARAGRAPH
        elif re.match(r'^[^:\s]+:\s*.*$', stripped_line):
            if in_metadata is True and metadata is False and index_of_line != -1:
                print('found METADATA')
                line = {'metadata': line}
                final_list.append(line)
                index_of_line += 1
            elif in_metadata is False and metadata is False and index_of_line != -1: # could the last expression lead to problems?
                previous_line: int = index_of_line - 1
                previous_dict: dict = final_list[previous_line]
                previous_key = list(previous_dict.keys())
                print(previous_key[0])
                previous_value = list(previous_dict.values())
                print(previous_value[0])
                if previous_key[0] == 'separator':
                    print(f'Current index: {index_of_line}')
                    print(f'Previous line: {previous_line}')
                    in_metadata = True
                    previous_dict = {'metadata': previous_value[0]}
                    final_list[previous_line] = previous_dict
                    line = {'metadata': line}
                    final_list.append(line)
                    index_of_line += 1
                else:
                    print('found PARAGRAPH')
                    line = {'paragraph': line}
                    final_list.append(line)
                    index_of_line += 1
            else: # TODO: proof this case can happen?
                print('found PARAGRAPH')
                line = {'paragraph': line}
                final_list.append(line)
                index_of_line += 1
        #elif stripped_line.strip() == '': # not empty paragraphs but problematic for lists
            #print('found EMPTY LINE')
            #continue
        else:
            # METADATA
            if in_metadata: # such a case will not make it into the metadata
                if stripped_line.strip() == '':
                    print('found EMPTY LINE in METADATA')
                    continue # TODO: This causes to have index_of_line += 1 in every if-else statement. Alternative?
                else:
                    print('found PARAGRAPH and ended METADATA')
                    in_metadata = False
                    line = {'paragraph': line}
                    final_list.append(line)
                    # set previous lines to correct key
                    final_list = reset_metdata(current_list=final_list)
                    index_of_line += 1
            elif metadata is True:
                print('found PARAGRAPH')
                line = {'paragraph': line}
                final_list.append(line) #
                index_of_line += 1
            elif stripped_line.strip() == '':
                print('found EMPTY LINE in METADATA')
                continue
            else:
                print('found PARAGRAPH')
                line = {'paragraph': line}
                final_list.append(line) #
                index_of_line += 1
        print(index_of_line)
        

    return final_list

rich.print(md_line_classification(markdown=markdown_example))

line_definition_output = [
    {'paragraph': ''},
    {'separator': '---'},
    {'metadata': 'title: Example'},
    {'separator': '---'},
    {'paragraph': ''},
    {'paragraph': 'Just text'},
    {'paragraph': ''},

    {'h1': '# Sample Markdown #Lists'},

    {'paragraph': ''},

    {'h2': '## Lists'},

    {'paragraph': ''},

    {'h3': '### Unordered Lists'},

    {'list': '- Item 1'},
    {'list': '- Item 2'},
    {'list': '    - Subitem 1'},
    {'list': '        - Subsubitem 1'},
    {'list': '    - Subitem 2'},
    {'list': '- Item 3'},

    {'paragraph': ''},

    {'list': '- Item 1'},
    {'list': '- Item 2'},

    {'paragraph': ''},

    {'code': '```Python'},
    {'paragraph': 'def hello_world():'},
    {'paragraph': "    print('Hello World!)"},
    {'code': '```'},

    {'paragraph': ''},

    {'h3': '### Ordered List'},

    {'list': '4. First item reversed'},
    {'list': '3. Second item'},
    {'list': '    1. Subitem 1'},
    {'list': '    2. Subitem 2'},
    {'list': '2. Third item'},

    {'paragraph': ''},

    {'list': '1. First item'},
    {'list': '2. Second item'},

    {'paragraph': ''},

    {'h2': '## Not a List'},

    {'paragraph': ''},
    {'paragraph': 'This is just regular text.'},
    {'paragraph': ''},
    {'paragraph': 'Again regular text'},
    {'paragraph': ''},

    {'h2': '## Table'},

    {'table': '| Column 1 | Column 2 |'},
    {'table': '|----------|----------|'},
    {'table': '| Cell 1   | Cell 2   |'},

    {'paragraph': ''},
    {'paragraph': 'A definition list'},

    {'def_list': ': The definition of a list'},
    {'def_list': ': The next line of the definition'},

    {'paragraph': ''}
]



################
# MERGE
################
def join_metadata_lines_properly(final_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
    result = []
    metadata_dict = {}
    in_metadata = False
    
    for item in final_list:
        if list(item.keys())[0] == 'metadata':
            if item['metadata'].strip() == '---':
                if in_metadata:
                    # End of metadata block
                    result.append({"metadata": metadata_dict})
                    in_metadata = False
                else:
                    # Start of metadata block
                    in_metadata = True
                    metadata_dict = {}
            elif in_metadata:
                # Process metadata line
                line = item['metadata'].strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if value.startswith('[') and value.endswith(']'):
                        # Parse list value
                        value = [v.strip() for v in value[1:-1].split(',')]
                    else:
                        # Keep as string
                        value = value
                    
                    metadata_dict[key] = value
        else:
            if in_metadata:
                # End of metadata block without a closing separator
                result.append({"metadata": metadata_dict})
                in_metadata = False
            
            # Add non-metadata item to the result
            result.append(item)
    
    # Handle case where metadata block ends without a separator
    if in_metadata:
        result.append({"metadata": metadata_dict})
    
    return result

def join_code_lines_properly(final_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
    '''
    Iterates over the final list and joines the code lines into a single line.
    It checks for starting ``` and ending ``` to join correctly.
    Each joined line gets separated by \n
    '''
    result = []
    in_code_block = False
    temp_code_block = []
    start_delimiter = None

    for item in final_list:
        if list(item.keys())[0] == 'code':
            if item['code'].startswith('```'):
                if in_code_block:
                    # End of code block
                    temp_code_block.append(item['code'])
                    result.append({'code': '\n'.join(temp_code_block)})
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
        result.append({'code': '\n'.join(temp_code_block)})
    return result

def join_list_lines_properly(final_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Iterates over each line and joins comprehensive list lines to one list dictionary.
    '''
    result = []
    in_list_block = False
    temp_list_block = []

    for item in final_list:
        if list(item.keys())[0] == 'list':
            if in_list_block:
                temp_list_block.append(item['list'])
            else:
                in_list_block = True
                temp_list_block.append(item['list'])
        else:
            if in_list_block:
                result.append({'list': '\n'.join(temp_list_block)})
                temp_list_block.clear()
                in_list_block = False
            result.append(item)

    # Handle any remaining list block
    if in_list_block:
        result.append({'list': '\n'.join(temp_list_block)})

    return result  

def join_def_list_lines_properly(final_list: List[Dict[str, Text | Any]]) -> List[Dict[str, Text | Any]]:
    result = []
    current_term = None
    current_definitions = []

    for item in final_list:
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


def join_table_lines_properly(final_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    for item in final_list:
        if list(item.keys())[0] == 'table':
            if in_table_block:
                if is_separator_row(item['table']) and len(temp_table_block) > 1:
                    # take last row
                    last_row = temp_table_block[-1]
                    temp_table_block.pop(-1)
                    # New table detected, finish the previous one
                    result.append({'table': '\n'.join(temp_table_block)})
                    temp_table_block = [last_row]
                temp_table_block.append(item['table'])
            else:
                in_table_block = True
                temp_table_block.append(item['table'])
        else:
            if in_table_block:
                if temp_table_block:
                    result.append({'table': '\n'.join(temp_table_block)})
                temp_table_block.clear()
                in_table_block = False
            result.append(item)

    # Handle any remaining table block
    if in_table_block and temp_table_block:
        result.append({'table': '\n'.join(temp_table_block)})

    return result

def join_blockquote_lines_properly(final_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    for item in final_list:
        if list(item.keys())[0] == 'blockquote':
            if not in_blockquote:
                in_blockquote = True
            temp_blockquote_content.append(item['blockquote'])
        else:
            if in_blockquote:
                result.append({'blockquote': '\n'.join(temp_blockquote_content)})
                temp_blockquote_content = []
                in_blockquote = False
            result.append(item)

    # Handle the case where the list ends with a blockquote
    if in_blockquote:
        result.append({'blockquote': '\n'.join(temp_blockquote_content)})

    return result

def md_join_lines_to_building_blocks(final_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Iterating over the list and merge patterns
    '''
    # TODO: missing
    # Metadata:
    final_list = join_metadata_lines_properly(final_list=final_list)
    # Lists: comprehensive lists are separated by every other building blocks.
    final_list = join_list_lines_properly(final_list=final_list)
    # Definition lists: 
    final_list = join_def_list_lines_properly(final_list=final_list)
    # Tables: be ware of |---|. This is giving information if there is a new table with new column header
    final_list = join_table_lines_properly(final_list=final_list)
    # Code: has to start with ``` and end with ```.
    final_list = join_code_lines_properly(final_list=final_list)
    # Blockquotes:
    final_list = join_blockquote_lines_properly(final_list=final_list)
    # Paragraphs: do not merge paragraphs but delete empty paragraphs. Why? -> because maybe later we want to specify paragraphs in pydantic



    return final_list

rich.print(md_join_lines_to_building_blocks(final_list=md_line_classification(markdown=markdown_example)))

excepted_output = [
    {'paragraph': ''},
    {'separator': '---'},
    {'metadata': 'title: Example'},
    {'separator': '---'},
    {'paragraph': '\nJust text\n'},

    {'h1': '# Sample Markdown #Lists'},

    {'paragraph': ''},

    {'h2': '## Lists'},

    {'paragraph': ''},

    {'h3': '### Unordered Lists'},

    {'list': '- Item 1\n- Item 2\n    - Subitem 1\n        - Subsubitem 1\n    - Subitem 2\n- Item 3'},
    
    {'paragraph': ''},

    {'list': '- Item 1\n- Item 2'},
    {'paragraph': ''},

    {'code': '```Python'},
    {'paragraph': 'def hello_world():\n    print("Hello World!")'},
    {'code': '```'},

    {'paragraph': ''},

    {'h3': '### Ordered List'},

    {'list': '4. First item reversed\n3. Second item\n    1. Subitem 1\n    2. Subitem 2\n2. Third item'},

    {'paragraph': ''},

    {'list': '1. First item\n2. Second item'},

    {'paragraph': ''},

    {'h2': '## Not a List'},

    {'paragraph': '\nThis is just regular text.\nAgain regular text\n'},

    {'h2': '## Table'},

    {'table': '| Column 1 | Column 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |'},

    {'paragraph': '\nA definition list'},
    {'def_list': ': The definition of a list\n: The next line of the definition'},

    {'paragraph': ''}
]


