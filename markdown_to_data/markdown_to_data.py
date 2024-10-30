from typing import List, Dict, Any, Literal
import json

from .convert.classification.classification import md_line_classification
from .convert.finalize import final_md_data_as_list, final_md_data_as_dict


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

    print(Markdown(markdown).md_dict)
    ```

    Ouput:
    ```
    {
        'A header': {
            'list_1': {
                'type': 'ul',
                'list': [['Item 1'], ['Item 2'], ['Item 3']]
            }
        }
    }
    ```

    With `print(Markdown(markdown).md_list)`
    ```
    [
        {'h1': 'A header'},
        {
            'list: {
                'type': 'ul',
                'list': [['Item 1'], ['Item 2'], ['Item 3']]
            }
        }
    ]
    ```
    '''
    def __init__(self, markdown: str):
        self.markdown: str = markdown
        self.md_list: List[Dict[str, Any]] = final_md_data_as_list(classified_list=md_line_classification(markdown=self.markdown)) # TODO: get rid of this logic
        self.md_dict: Dict[str, Any] = final_md_data_as_dict(md_line_classification(markdown=self.markdown))


    def md_to_json(self, indent: int | str | None =None): # TODO: necessary?
        '''
        Convert the dictionary `markdown_dict` into JSON.
        '''
        return json.dumps(obj=self.md_list, indent=indent)

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
