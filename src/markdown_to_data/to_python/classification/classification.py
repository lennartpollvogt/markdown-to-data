from typing import Text, Any, List, Dict

from .md_classification.classify_md_code import set_line_keys_to_code
from .md_classification.classify_md_list import is_ordered_list_item, is_unordered_list_item
from .md_classification.classify_md_paragraph import is_paragraph
from .md_classification.classify_md_blockquote import is_blockquote
from .md_classification.classify_md_header import is_header_or_paragraph
from .md_classification.classify_md_separator import is_separator
from .md_classification.classify_md_table_row import is_table_row
from .md_classification.classify_md_definition_list import is_definition_list_item

from .line_content_classification import classify_line_content

def classify_markdown_line_by_line(markdown: Text) -> List[Dict[str, Any]]:

    markdown = markdown.lstrip() # delete whitespace from beginning
    lines: List[Text] = markdown.splitlines()
    classified_list: List[Dict[str, Any]] = []

    # INDEX
    index_of_line: int = -1
    # METADATA
    #in_metadata: bool = False
    #metadata: bool = False
    # CODE
    in_code: bool = False


    for line in lines:

        stripped_line = line.strip()
        indent = len(line) - len(line.lstrip())

        # CODE
        if stripped_line.startswith('```'):
            if in_code is False:
                line = {'code': line, 'indent': indent}
                classified_list.append(line)
                in_code = True
                index_of_line += 1
            elif in_code is True:
                line = {'code': line, 'indent': indent}
                classified_list.append(line)
                classified_list = set_line_keys_to_code(current_list=classified_list)
                in_code = False
                index_of_line += 1
            continue

        # IN CODE BLOCK
        if in_code:
            # Process as code regardless of content
            classified_list.append({'code': line, 'indent': indent})
            index_of_line += 1
            continue

        # SEPARATOR
        if is_separator(stripped_line):
            classified_list.append({'hr': '---', 'indent': indent})
            index_of_line += 1
            continue

        # UNORDERED LIST
        is_ul, ul_value, ul_marker, ul_task, ul_item_indent, ul_marker_indent = is_unordered_list_item(stripped_line, line)
        if is_ul:
            classified_list.append({
                'ul': {
                    'li': ul_value,
                    'marker': ul_marker,
                    'task': ul_task
                },
                'item_indent': ul_item_indent,
                'marker_indent': ul_marker_indent
            })
            index_of_line += 1
            continue

        # ORDERED LIST
        is_ol, ol_value, ol_marker, ol_task, ol_item_indent, ol_marker_indent = is_ordered_list_item(stripped_line, line)
        if is_ol:
            classified_list.append({
                'ol': {
                    'li': ol_value,
                    'marker': ol_marker,
                    'task': ol_task
                },
                'item_indent': ol_item_indent,
                'marker_indent': ol_marker_indent
            })
            index_of_line += 1
            continue

        # HEADER or PARAGRAPH
        if stripped_line.startswith('#'):
            result = is_header_or_paragraph(stripped_line=stripped_line, line=line, indent=indent)
            classified_list.append(result)
            index_of_line += 1
            continue

        # TABLES
        is_row, row_data = is_table_row(line)
        if is_row:
            classified_list.append(row_data)
            index_of_line += 1
            continue

        # BLOCKQUOTES
        is_bq, blockquote_dict = is_blockquote(line=line)
        if is_bq:
            classified_list.append(blockquote_dict)
            index_of_line += 1
            continue

        # DEFINITION LISTS
        previous_dict = (classified_list[-1] if classified_list and index_of_line > 0
                        else {'p': line, 'indent': indent})
        is_def_item, def_item_dict = is_definition_list_item(line, previous_dict)

        if is_def_item:
            if 'convert_previous' in def_item_dict:
                if classified_list:
                    classified_list[-1] = def_item_dict['convert_previous']
                else:
                    classified_list.append(def_item_dict['convert_previous'])
                classified_list.append(def_item_dict['current'])
            else:
                classified_list.append(def_item_dict)
            index_of_line += 1
            continue

        else:
            classified_list.append(is_paragraph(line, indent))
            index_of_line += 1

    return classified_list

def md_classification(markdown: Text, inline_classification: bool = True) -> List[Dict[str, Any]]:
    """
    Classify markdown text line by line and mark inline markdown elements.

    Args:
        markdown (Text): Raw markdown text to be classified
        inline_classification (bool): Whether to classify inline markdown elements. Defaults to True.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing classified markdown elements with their properties
    """
    classified_md = classify_markdown_line_by_line(markdown=markdown)

    if inline_classification:
        classified_md = classify_line_content(classified_lines=classified_md)

    return classified_md
