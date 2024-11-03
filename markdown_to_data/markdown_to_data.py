from typing import List, Dict, Any, Literal
import json

from .to_data.classification.classification import md_line_classification
from .to_data.finalize import final_md_data_as_list, final_md_data_as_dict


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
        if self._md_elements is None:
            if self._md_list is None:
                self._md_elements = list(set(key for item in self.md_list for key in item.keys()))
            else:
                self._md_elements = list(set(key for item in self._md_list for key in item.keys()))
        return self._md_elements

    def md_to_json(self, indent: int | str | None =None): # TODO: necessary?
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
