from typing import List, Dict, Any, Literal, Text
import json

# TO DATA
from .to_data.classification.classification import md_line_classification
from .to_data.finalize import final_md_data_as_list, final_md_data_as_dict
# TO MD
from .to_md.to_md_parser import to_md_parser
from .to_md.md_elements_list import MDElements

class Markdown:
    def __init__(self, markdown: str):
        self._markdown = markdown
        self._classified_lines = None
        self._md_list = None
        self._md_dict = None
        self._md_elements = None

    @property
    def classified_lines(self):
        if self._classified_lines is None:
            self._classified_lines = md_line_classification(self._markdown)
        return self._classified_lines

    @property
    def md_list(self):
        if self._md_list is None:
            self._md_list = final_md_data_as_list(self.classified_lines)
        return self._md_list

    @property
    def md_dict(self):
        if self._md_dict is None:
            self._md_dict = final_md_data_as_dict(self.classified_lines)
        return self._md_dict

    @property
    def md_elements(self):
        '''
        Get information about all markdown elements in the markdown file.
        The output is based on `md_list` and can be used for navigate through `md_list`

        Returns:
            A dictionary containing information about each markdown element type:
                - count: Number of occurrences of the element
                - positions: List of indices where the element appears within the `md_list` object
                - variants: Set of different types/formats for applicable elements
                    - For lists: 'ul' (unordered) or 'ol' (ordered)
                    - For code blocks: Programming language or None
                    - Empty set() for elements without variants

        Example:
            {
                'list': {
                    'count': 3,
                    'positions': [5, 10, 12],
                    'variants': {'ul', 'ol'}
                },
                'code': {
                    'count': 4,
                    'positions': [2, 3, 21, 22],
                    'variants': {'python', None}
                },
                'blockquote': {
                    'count': 4,
                    'positions': [17, 18, 27, 28],
                    'variants': set()
                }
            }
        '''
        if self._md_elements is None:
            elements_info = {}
            for item in self.md_list:
                for key in item.keys():
                    if key not in elements_info:
                        elements_info[key] = {
                            'count': 0,
                            'positions': [],
                            'variants': set()
                        }

                    elements_info[key]['count'] += 1
                    elements_info[key]['positions'].append(self.md_list.index(item))

                    # Collect specific variants/types
                    if key == 'list':
                        elements_info[key]['variants'].add(item[key]['type'])  # 'ul' or 'ol'
                    elif key == 'code':
                        elements_info[key]['variants'].add(item[key]['language'])  # language type or None

            self._md_elements = elements_info
        return self._md_elements

    def to_md(self, include: List[MDElements | int] = ['all'], exclude: List[MDElements | int] | None = None, spacer: int = 1) -> Text:
        '''
        Parse the markdown data back to markdown formatted string.

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
        '''
        return to_md_parser(data=self.md_list, include=include, exclude=exclude, spacer=spacer)

    def to_json(self, indent: int | str | None =None): # TODO: necessary?
        '''
        Convert the dictionary `markdown_dict` into JSON.
        '''
        return json.dumps(obj=self.md_dict, indent=indent)


    def get_md_building_blocks(self, blocks: List[Literal['table', 'list', 'blockquote', 'def_list', 'metadata', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'paragraph']], format: Literal['python', 'json']='python') -> List[Dict[str, Any]]:
        '''
        Return the set buildings blocks of the markdown as python dictionary or json (string)
        '''
        #md_list = self._markdown_to_data(hierarchy=False)
        building_blocks: List[Dict[str, Any]] = []

        #for item in md_list:
        for item in self.md_list:
            for key in item:
                if key in blocks:
                    building_blocks.append(item)

        return building_blocks
