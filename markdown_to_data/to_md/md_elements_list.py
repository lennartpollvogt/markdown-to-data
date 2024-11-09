from typing import Literal, Union

HeaderTypes = Literal['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

MDElements = Union[
    Literal[
        'metadata',
        'headers',
        'paragraph',
        'blockquote',
        'list',
        'def_list',
        'table',
        'code',
        'separator',
        'all'
    ],
    HeaderTypes
]
