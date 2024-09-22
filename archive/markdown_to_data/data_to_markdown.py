'''
This file contains the functions to convert data into markdown
- html into markdown
- python, json, yaml or xml to markdown
- python, json, yaml or xml to lists (? NOT SURE ?)


'''

from typing import Dict, Any, List, Text

def html_to_md(
        # url, file, text
):
    '''
    Could be used with the Markdown class:
    ```python
    from markdown_to_data import Markdown, html_to_md

    markdown = Markdown(markdown=html_to_md('https://example.com'))
    ```
    '''
    
    # maybe easier to convert directly into markdown instead python
    pass

def python_to_md(
        data: List[List[Dict[str, Any]]] | List[Dict[str, Any]] | List[Any] | Dict[str, Any],
    ) -> Text:
    # convert a python object into markdown table (or a list?)

    pass

def xml_to_md(
        # url, file, text
) -> Text:
    # convert it to a python dict
    # uses dict_to_md() to convert it to md
    pass

def json_to_md(
        # URL, file, text
) -> Text:
    # converts into a python dict
    # uses python_to_md() to convert it to md
    pass

def yaml_to_md(
        # URL, file, text
) -> Text:
    # converts into a python dict
    # uses python_to_md() to convert it to md
    pass