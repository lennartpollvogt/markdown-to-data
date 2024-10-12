from typing import List, Dict, Any, Literal
import json

from .convert.classification.classification import md_line_classification
from .convert.finalize import final_md_data_as_list


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
    def __init__(self, markdown: str, hierarchy: bool = False):
        self.markdown: str = markdown
        self.hierarchy: bool = hierarchy
        self.markdown_list = self._markdown_to_data()
        #self.markdown_list = self._markdown_to_data()
        #List[Dict[str, Any]]
        
        #self._markdown_to_data()
        

    def _markdown_to_data(self, hierarchy: bool | None = None) -> Dict[str, Any]:
        '''
        Based on a given markdown it returns the converted python dictionary and stores it into the class variable `self.markdown_dict`.

        Args:
            - hierarchy: If the hierarchy of the markdown should be considered
        '''
        if not isinstance(self.markdown, str):
            what_type = type(self.markdown)
            raise TypeError(f"Expected a string for arg 'markdown'. Got {what_type}")
        #self.markdown_list = final_md_data_as_list(classified_list=md_line_classification(markdown=self.markdown), hierarchy=self.hierarchy)
        if hierarchy is None:
            hierarchy = self.hierarchy
        result = final_md_data_as_list(classified_list=md_line_classification(markdown=self.markdown), hierarchy=hierarchy)
        return result

    def md_to_json(self, indent: int | str | None =None):
        '''
        Convert the dictionary `markdown_dict` into JSON.
        '''
        return json.dumps(obj=self.markdown_list, indent=indent)
    
    def get_md_building_blocks(self, blocks: List[Literal['table', 'list', 'blockquote', 'def_list', 'metadata', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'paragraph']], format: Literal['python', 'json']='python') -> List[Dict[str, Any]] | str:
        '''
        Return the set buildings blocks of the markdown as python dictionary or json (string)
        '''
        md_list = self._markdown_to_data(hierarchy=False)
        building_blocks: List[Dict[str, Any]] = []

        for item in md_list:
            for key in item:
                if key in blocks:
                    building_blocks.append(item)
        
        return building_blocks
                    
