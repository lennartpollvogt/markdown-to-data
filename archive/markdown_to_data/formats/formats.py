'''
Defining the responses formats
'''

from typing import Literal


# for conversion
FORMATS = Literal[
    'python', 
    'json',
    'yaml',
    'xml'
]

# for pydantic models
DATA_TYPES = Literal[
    'tables',
    'lists'
]