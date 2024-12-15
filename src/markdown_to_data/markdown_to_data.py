from typing import List, Dict, Any, Literal, Text
import json

# TO PYTHON
from .to_python.classification.classification import md_classification
from .to_python.to_python_objects import merge_classified_markdown_lines, hierarchy_with_merged_markdown_lines
# TO MD
from .to_md.to_md_parser import to_md_parser
from .to_md.md_elements_list import MDElements

class Markdown:
    """
    A class for parsing markdown text into structured data formats and back to markdown.

    This class provides functionality to:
    1. Parse markdown text into structured Python objects (lists and dictionaries)
    2. Extract information about markdown elements and their structure
    3. Convert parsed markdown back to formatted text
    4. Extract specific markdown building blocks

    The class uses lazy loading for its properties, computing them only when first accessed.

    Attributes:
        classified_lines (List[Dict]): Raw classification of markdown lines with type and indentation information
        md_list (List[Dict]): Structured list representation of markdown elements
        md_dict (Dict): Hierarchical dictionary representation using headers as keys
        md_elements (Dict): Information about markdown element types, counts, and positions

    Supported Markdown Elements:
        - Metadata (YAML frontmatter)
        - Headers (h1-h6)
        - Lists (ordered, unordered, and task lists with nesting)
        - Tables (with and without headers)
        - Code blocks (with language detection)
        - Definition lists
        - Blockquotes (with nesting)
        - Paragraphs
        - Horizontal rules (separators)

    Example:
        ```python
        markdown_text = '''
        # Header

        - List item 1
        - List item 2
            - Nested item

        ```python
        print("Hello")
        ```
        '''

        md = Markdown(markdown_text)

        # Get structured list representation
        print(md.md_list)

        # Get hierarchical dictionary
        print(md.md_dict)

        # Get information about markdown elements
        print(md.md_elements)

        # Convert back to markdown
        print(md.to_md())

        # Extract specific blocks
        print(md.get_md_building_blocks(['code', 'list']))
        ```

    Notes:
        - The class preserves the structure and hierarchy of the original markdown
        - Inline formatting (bold, italic, links) is currently not parsed
        - Task list items support checked ([x]) and unchecked ([ ]) states
        - Tables are stored in a column-based format for easier data manipulation
        - Code blocks preserve language information when specified

    See Also:
        - to_md_parser: For direct conversion of markdown data structures to text
        - MDElements: For list of supported markdown element types
    """
    def __init__(self, markdown: str):
        self._markdown = markdown
        self._classified_lines = None
        self._md_list = None
        self._md_dict = None
        self._md_elements = None

    @property
    def classified_lines(self):
        if self._classified_lines is None:
            self._classified_lines = md_classification(markdown=self._markdown, inline_classification=True) #md_line_classification(self._markdown)
        return self._classified_lines

    @property
    def md_list(self):
        if self._md_list is None:
            self._md_list = merge_classified_markdown_lines(classified_list=self.classified_lines) # final_md_data_as_list(self.classified_lines)
        return self._md_list

    @property
    def md_dict(self):
        if self._md_dict is None:
            self._md_dict = hierarchy_with_merged_markdown_lines(self.md_list)
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

    # TODO: needs reworks
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

    def to_json(self, indent: int | str | None = None): # TODO: necessary?
        '''
        Convert the dictionary `markdown_dict` into JSON.
        '''
        return json.dumps(obj=self.md_dict, indent=indent)


    # TODO: 'checked', 'unchecked' to exclude checked or unchecked task list elements
    def get_md_building_blocks(self, blocks: List[Literal['table', 'list', 'blockquote', 'def_list', 'metadata', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'paragraph']], format: Literal['python', 'json']='python') -> List[Dict[str, Any]] | str:
        """
        Extract specific markdown building blocks from the document.

        Args:
            blocks: List of markdown element types to extract
            format: Output format ('python' or 'json')

        Returns:
            List of dictionaries containing the requested markdown elements,
            or JSON string if format='json'
        """
        building_blocks: List[Dict[str, Any]] = []

        # Create a mapping for header levels to requested header types
        header_levels = {
            int(block[1]) for block in blocks
            if block.startswith('h') and block[1].isdigit()
        }

        # Create a set of non-header block types for faster lookup
        regular_blocks = {block for block in blocks if not block.startswith('h')}

        for item in self.md_list:
            # Handle headers
            if 'header' in item and item['header']['level'] in header_levels:
                building_blocks.append(item)
                continue

            # Handle all other block types
            for key in item:
                if key in regular_blocks:
                    building_blocks.append(item)
                    break

        # Return in requested format
        if format == 'json':
            return json.dumps(building_blocks)
        return building_blocks
