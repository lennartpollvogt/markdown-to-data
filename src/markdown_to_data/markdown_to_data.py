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
        md_elements (Dict): Comprehensive information about markdown element types, counts, positions, variants, and summary statistics

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

        # Get comprehensive information about markdown elements
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
        - md_elements provides enhanced analytics including variant tracking, summary statistics,
          and performance-optimized indexing for navigation and analysis

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
        Get comprehensive information about all markdown elements in the markdown file.
        The output is based on `md_list` and can be used to navigate through `md_list`

        Returns:
            A dictionary containing information about each markdown element type:
                - count: Number of occurrences of the element
                - positions: List of indices where the element appears within the `md_list` object
                - variants: Set of different types/formats for applicable elements
                    - For lists: 'ul' (unordered), 'ol' (ordered), or 'task' variants
                    - For code blocks: Programming language or None
                    - For headers: 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
                    - For tables: Column count variants
                    - Empty set() for elements without variants
                - summary: Additional summary statistics for certain elements
                    - For tables: Set of column counts, total cells
                    - For lists: Task list statistics (checked/unchecked counts)
                    - For blockquotes: Nesting depth information
        '''
        if self._md_elements is None:
            elements_info = {}

            # Fields to exclude from elements analysis
            EXCLUDED_FIELDS = {'start_line', 'end_line'}

            # Use enumerate to fix O(n²) performance issue
            for index, item in enumerate(self.md_list):
                for key, value in item.items():
                    # Skip line number fields
                    if key in EXCLUDED_FIELDS:
                        continue
                    if key not in elements_info:
                        elements_info[key] = {
                            'count': 0,
                            'positions': [],
                            'variants': set(),
                            'summary': {}
                        }

                    elements_info[key]['count'] += 1
                    elements_info[key]['positions'].append(index)

                    # Enhanced variant tracking and summary statistics
                    if key == 'list':
                        list_type = value['type']
                        elements_info[key]['variants'].add(list_type)

                        # Check for task lists and collect statistics
                        task_stats = self._analyze_list_tasks(value['items'])
                        if task_stats['has_tasks']:
                            elements_info[key]['variants'].add('task')
                            if 'task_stats' not in elements_info[key]['summary']:
                                elements_info[key]['summary']['task_stats'] = {
                                    'checked': 0, 'unchecked': 0, 'total_tasks': 0
                                }
                            elements_info[key]['summary']['task_stats']['checked'] += task_stats['checked']
                            elements_info[key]['summary']['task_stats']['unchecked'] += task_stats['unchecked']
                            elements_info[key]['summary']['task_stats']['total_tasks'] += task_stats['total_tasks']

                    elif key == 'code':
                        lang = value.get('language')
                        elements_info[key]['variants'].add(lang)

                        # Add code statistics
                        if 'languages' not in elements_info[key]['summary']:
                            elements_info[key]['summary']['languages'] = {}
                        lang_key = lang if lang else 'no_language'
                        elements_info[key]['summary']['languages'][lang_key] = \
                            elements_info[key]['summary']['languages'].get(lang_key, 0) + 1

                    elif key == 'header':
                        level = value['level']
                        elements_info[key]['variants'].add(f"h{level}")

                        # Track header level distribution
                        if 'levels' not in elements_info[key]['summary']:
                            elements_info[key]['summary']['levels'] = {}
                        elements_info[key]['summary']['levels'][level] = \
                            elements_info[key]['summary']['levels'].get(level, 0) + 1

                    elif key == 'table':
                        if isinstance(value, dict):
                            col_count = len(value.keys())
                            elements_info[key]['variants'].add(f"{col_count}_columns")

                            # Calculate table statistics
                            total_cells = sum(len(col_data) if isinstance(col_data, list) else 1
                                            for col_data in value.values())

                            if 'column_counts' not in elements_info[key]['summary']:
                                elements_info[key]['summary']['column_counts'] = set()
                            if 'total_cells' not in elements_info[key]['summary']:
                                elements_info[key]['summary']['total_cells'] = 0

                            elements_info[key]['summary']['column_counts'].add(col_count)
                            elements_info[key]['summary']['total_cells'] += total_cells

                    elif key == 'blockquote':
                        # Analyze blockquote nesting depth
                        max_depth = self._analyze_blockquote_depth(value)
                        elements_info[key]['variants'].add(f"depth_{max_depth}")

                        if 'max_nesting_depth' not in elements_info[key]['summary']:
                            elements_info[key]['summary']['max_nesting_depth'] = 0
                        elements_info[key]['summary']['max_nesting_depth'] = \
                            max(elements_info[key]['summary']['max_nesting_depth'], max_depth)

                    elif key == 'def_list':
                        # Track definition list statistics
                        if isinstance(value, dict) and 'list' in value:
                            def_count = len(value['list']) if isinstance(value['list'], list) else 1
                            elements_info[key]['variants'].add(f"{def_count}_definitions")

                    elif key == 'metadata':
                        # Track metadata field count
                        if isinstance(value, dict):
                            field_count = len(value.keys())
                            elements_info[key]['variants'].add(f"{field_count}_fields")

            # Convert sets to sorted lists for consistent output
            for element_type in elements_info:
                # Handle None values in variants by filtering them out and sorting separately
                variants_list = list(elements_info[element_type]['variants'])
                none_variants = [v for v in variants_list if v is None]
                non_none_variants = [v for v in variants_list if v is not None]

                # Sort non-None variants and append None variants at the end
                sorted_variants = sorted(non_none_variants) + none_variants
                elements_info[element_type]['variants'] = sorted_variants

                if 'column_counts' in elements_info[element_type]['summary']:
                    elements_info[element_type]['summary']['column_counts'] = \
                        sorted(list(elements_info[element_type]['summary']['column_counts']))

            self._md_elements = elements_info
        return self._md_elements

    def _analyze_list_tasks(self, items, depth=0):
        """Recursively analyze list items to count tasks and determine task list presence."""
        stats = {'has_tasks': False, 'checked': 0, 'unchecked': 0, 'total_tasks': 0}

        for item in items:
            if isinstance(item, dict):
                if item.get('task') == 'checked':
                    stats['has_tasks'] = True
                    stats['checked'] += 1
                    stats['total_tasks'] += 1
                elif item.get('task') == 'unchecked':
                    stats['has_tasks'] = True
                    stats['unchecked'] += 1
                    stats['total_tasks'] += 1

                # Recursively check nested items
                if 'items' in item and item['items']:
                    nested_stats = self._analyze_list_tasks(item['items'], depth + 1)
                    if nested_stats['has_tasks']:
                        stats['has_tasks'] = True
                        stats['checked'] += nested_stats['checked']
                        stats['unchecked'] += nested_stats['unchecked']
                        stats['total_tasks'] += nested_stats['total_tasks']

        return stats

    def _analyze_blockquote_depth(self, blockquote_data, current_depth=1):
        """Recursively analyze blockquote nesting to find maximum depth."""
        max_depth = current_depth

        if isinstance(blockquote_data, list):
            for item in blockquote_data:
                if isinstance(item, dict) and 'items' in item:
                    if item['items']:  # Has nested blockquotes
                        nested_depth = self._analyze_blockquote_depth(item['items'], current_depth + 1)
                        max_depth = max(max_depth, nested_depth)

        return max_depth

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
