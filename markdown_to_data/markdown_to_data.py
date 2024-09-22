from typing import List, Dict, Any, Text
import json

from .utils.classification import md_line_classification
from .utils.merging import md_join_lines_to_building_blocks


class Markdown():
    '''
    The `Markdown` class to convert a structured markdown text into processable data.
    Pass the markdown as argument into the function and get back the dictionary with `Markdown(markdown).markdown_dict`.

    Example of `markdown_dict`:
    ```python
    from markdown_to_data import Markdown

    markdown = """
    # A header

    - Item 1
    - Item 2
    - Item 3
    """

    print(Markdown(markdown).markdown_dict)
    ```

    Ouput:
    ```
    {"h1_1": {"heading": "A header", "list_1": {"type": "ul", "list": [["Item 1"], ["Item 2"], ["Item 3"]]}}}
    ```
    '''
    def __init__(self, markdown: str):
        self.markdown: str = markdown
        self.markdown_dict: List[Dict[str, Any]]
        self._markdown_to_data()

    def _markdown_to_data(self) -> Dict[str, Any]:
        '''
        Based on a given markdown it returns the converted python dictionary and stores it into the class variable `self.markdown_dict`.
        '''
        if not isinstance(self.markdown, str):
            what_type = type(self.markdown)
            raise TypeError(f"Expected a string for arg 'markdown'. Got {what_type}")
        data = md_join_lines_to_building_blocks(final_list=md_line_classification(markdown=self.markdown))
        self.markdown_dict = data

    def md_to_json(self):
        '''
        Convert the dictionary `markdown_dict` into JSON.
        '''
        return json.dumps(obj=self.markdown_dict)