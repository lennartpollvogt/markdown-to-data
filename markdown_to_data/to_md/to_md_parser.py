'''
Includes the main function to parse `md_list` OR `md_dict` to markdown.
The function comes with arguments to specify the markdown output.

Examples for arguments:
data = self.md_list OR self.md_dict
include = Literal; building blocks to include (if provided, only include them; default "all")
exclude = Literal; building blocks to exclude (if provided, the specific building blocks get excluded from response; default `None`);
--> `exclude` beats `include`!
space = lines between buildings blocks

If `md_dict` is provided, and h1 is excluded, all children entries of the h1 dict are excluded as well.
'''

from typing import Literal, List, Dict, Text, Any, get_args

from .md_elements_list import MDElements, HeaderTypes
from .md_elements.to_md_metadata import metadata_data_to_md
from .md_elements.to_md_paragraphs import paragraph_data_to_md
from .md_elements.to_md_blockquotes import blockquote_data_to_md
from .md_elements.to_md_lists import list_data_to_md
from .md_elements.to_md_def_lists import definition_list_data_to_md
from .md_elements.to_md_code import code_data_to_md
from .md_elements.to_md_tables import table_data_to_md
from .md_elements.to_md_headers import header_data_to_md
from .md_elements.to_md_separator import separator_data_to_md

def to_md_parser(
    data: List[Dict[str, Any]],
    include: List[MDElements] = ['all'],
    exclude: List[MDElements] | None = None,
    spacer: int = 1
) -> Text:
    """
    Parse list of dictionaries into markdown format.

    Args:
        data: List of dictionaries containing markdown elements
        include: Element types to include (default 'all')
        exclude: Element types to exclude (overrides include if same values are listed)
        spacer: Number of empty lines between elements

    Returns:
        Formatted markdown string

    If a list of markdown element types for `include` is provided, only those markdown element types will be parsed.
    'all' means, all the markdown elements will be parsed. This is the default.

    If a list of markdown element types for `exclude` is provided, those markdown element types will be excluded.
    If the same markdown element type is provided in `include` and `exclude`, `exclude` is the dominant argument and the markdown element type will be excluded from the output.

    The integer for spacer must be 0 or positive. It defines the namer of empty lines which will be added after each parsed markdown element.
    0 spacer means not empty lines.
    2 spacer means 2 empty lines.
    """
    if not isinstance(data, list):
            return ''

    # Early return if 'all' is in exclude
    if exclude and 'all' in exclude:
        return ''

    markdown_parts = []

    # Create mapping of element types to their parser functions
    parser_map = {
        'metadata': metadata_data_to_md,
        'paragraph': paragraph_data_to_md,
        'blockquote': blockquote_data_to_md,
        'list': list_data_to_md,
        'def_list': definition_list_data_to_md,
        'code': code_data_to_md,
        'table': table_data_to_md,
        'separator': separator_data_to_md
    }

    # Headers are handled specially due to multiple types
    header_types = list(get_args(HeaderTypes))

    # Process include/exclude logic
    excluded_elements = set()
    if exclude:
        excluded_elements = set(exclude)
        if 'headers' in excluded_elements:
            excluded_elements.update(header_types)

    included_elements = set()
    if 'all' not in include:
        included_elements = set(include)
        if 'headers' in included_elements:
            included_elements.update(header_types)

    # Process each item in the data list
    valid_elements = []

    for item in data:
        if not item or not isinstance(item, dict):
            continue

        element_type, content = next(iter(item.items()))

        # First check exclusions
        if element_type in excluded_elements or \
            (element_type in header_types and 'headers' in excluded_elements):
            continue

        # Then check inclusions
        if 'all' not in include and not (
            element_type in included_elements or \
            (element_type in header_types and 'headers' in included_elements)
        ):
            continue

        # Process the element
        if element_type in header_types:
            parsed_content = header_data_to_md({element_type: content})
        elif element_type in parser_map:
            parsed_content = parser_map[element_type](content)
        else:
            continue

        if parsed_content:
            valid_elements.append(parsed_content)

    # Join elements with proper spacing
    if not valid_elements:
        return ''

    if spacer == 0:
        return '\n'.join(valid_elements)
    else:
        spacing = '\n' * (spacer + 1)
        return spacing.join(valid_elements)
