import yaml # with pyyaml
from dict2xml import dict2xml
import json
from typing import List, Dict, Any, Text
from pydantic import BaseModel


# internal imports
from .formats.formats import DATA_TYPES, FORMATS
from .formats.tables import extract_tables_from_markdown
from .formats.lists import extract_lists_from_markdown, lists_to_xml


class Markdown:
    '''
    
    '''
    def __init__(self, markdown: Text):
        self.markdown: Text = markdown
        self.markdown_dict: Dict[str, Any] # used to convert in any data format (JSON, YAML, XML)
        # self.json_schema: Dict[str, Any] # create a JSON schema for Validation
        self.pydantic_model: BaseModel # used to make pydantics functionality available
    

    def md_headers(self, format: FORMATS = 'python', indent: int | None = None) -> List[List[Dict[str, Any]]] | List[Any] | Text:
        '''
        Get all the headers in their hierarchical structure in the given format.
        '''
        pass

    def md_tables(self, format: FORMATS = 'python', indent: int | None = None) -> List[List[Dict[str, Any]]] | List[Any] | Text:
        '''
        Based on the `format` it will return an object of the extracted tables.
        '''
        list_of_tables: List[List[Dict[str, Any]]] = extract_tables_from_markdown(markdown=self.markdown)
        if format == 'python':
            tables = list_of_tables
        elif format == 'json':
            tables = json.dumps(list_of_tables, indent=indent)
        elif format == 'yaml':
            tables = yaml.dump(data=list_of_tables, indent=indent, sort_keys=False)
        elif format == 'xml':
            if indent is not None and indent is int:
                indent: str = indent*" "
            tables = dict2xml(data=list_of_tables, wrap='table', indent=indent)
        return tables

    def md_lists(self, format: FORMATS = 'python', indent: int | None = None) -> List[list] | Text:
        '''
        Base on the `format` it will return a python list or json array of the extracted lists.
        '''
        list_of_lists: List[List[Any]] = extract_lists_from_markdown(markdown=self.markdown)
        if format == 'python':
            lists = list_of_lists
        elif format == 'json':
            lists = json.dumps(list_of_lists, indent=indent)
        elif format == 'yaml':
            lists = yaml.dump(data=list_of_lists, indent=indent, sort_keys=False)
        elif format == 'xml':
            lists = lists_to_xml(lists=list_of_lists, indent=indent)

        return lists

    def md_codes(self, format: FORMATS = 'python'):
        '''
        
        '''
        pass

    def md_urls(self, format: FORMATS = 'python'):
        '''
        ["url": "https://example.com/1", "alias": "example", "base_url": "https://example.com"]
        
        '''

    def markdown_structure(self, format: FORMATS = 'python'):
        '''
        Get the full markdown structure with headers, tables, paragraphs, codes, lists, etc.
        '''
        pass

    def pydantic_models(data_type: DATA_TYPES = 'tables') -> List[BaseModel]: # TODO: or give back a dictionary with the correct order
        '''
        Generate, base on the data_type, for each table or list a pydantic BaseModel.

        '''
        pass


