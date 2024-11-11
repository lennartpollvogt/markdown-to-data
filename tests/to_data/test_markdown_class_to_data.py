import pytest
from markdown_to_data.markdown_to_data import Markdown

def test_metadata():
    metadata = '''
---
title: Document
author: John Doe
date: 2023-12-20
---
'''
    md = Markdown(metadata)
    expected_dict = {
        'metadata': {
            'title': 'Document',
            'author': 'John Doe',
            'date': '2023-12-20'
        }
    }
    expected_list = [expected_dict]

    assert md.md_dict == expected_dict
    assert md.md_list == expected_list

def test_headers():
    headers = '''
# Heading level 1
## Heading level 2
## Heading level 2
### Heading level 3
# Heading level 1 again
'''
    md = Markdown(headers)
    expected_list = [
        {'h1': 'Heading level 1'},
        {'h2': 'Heading level 2'},
        {'h2': 'Heading level 2'},
        {'h3': 'Heading level 3'},
        {'h1': 'Heading level 1 again'}
    ]
    expected_dict = {
        'Heading level 1': {'Heading level 2': {'Heading level 3': {}}},
        'Heading level 1 again': {}
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_lists():
    lists = '''
- item 1
- item 2
    - subitem 1
    - subitem 2
- item 3

1. item 1
2. item 2
3. item 3
'''
    md = Markdown(lists)
    expected_list = [
        {
            'list': {
                'type': 'ul',
                'list': ['item 1', {'item 2': ['subitem 1', 'subitem 2']}, 'item 3']
            }
        },
        {'list': {'type': 'ol', 'list': ['item 1', 'item 2', 'item 3']}}
    ]
    expected_dict = {
        'list': {
            'type': 'ul',
            'list': ['item 1', {'item 2': ['subitem 1', 'subitem 2']}, 'item 3']
        },
        'list2': {'type': 'ol', 'list': ['item 1', 'item 2', 'item 3']}
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_tables():
    tables = '''
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
'''
    md = Markdown(tables)
    expected_list = [
        {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]},
        {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}
    ]
    expected_dict = {
        'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],
        'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_code():
    code = '''
```
{'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}
```

```python
def hello():
    print('Hello World!')
```
'''
    md = Markdown(code)
    expected_list = [
        {
            'code': {
                'language': None,
                'content': "{'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}"
            }
        },
        {
            'code': {
                'language': 'python',
                'content': "def hello():\n    print('Hello World!')"
            }
        }
    ]
    expected_dict = {
        'code': {
            'language': None,
            'content': "{'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}"
        },
        'code2': {
            'language': 'python',
            'content': "def hello():\n    print('Hello World!')"
        }
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_definition_lists():
    def_lists = '''
term 1
: definition 1
: definition 2

term 2
: definition 1
: definition 2
'''
    md = Markdown(def_lists)
    expected_list = [
        {'def_list': {'term': 'term 1', 'list': ['definition 1', 'definition 2']}},
        {'def_list': {'term': 'term 2', 'list': ['definition 1', 'definition 2']}}
    ]
    expected_dict = {
        'def_list': {'term': 'term 1', 'list': ['definition 1', 'definition 2']},
        'def_list2': {'term': 'term 2', 'list': ['definition 1', 'definition 2']}
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_blockquotes():
    blockquotes = '''
> a single line blockquote

> a nested blockquote
> with multiline
>> the nested part
> last line of the blockquote
'''
    md = Markdown(blockquotes)
    expected_list = [
        {'blockquote': ['a single line blockquote']},
        {
            'blockquote': [
                'a nested blockquote',
                {
                    'with multiline': [
                        'the nested part'
                    ]
                },
                'last line of the blockquote'
            ]
        }
    ]
    expected_dict = {
        'blockquote': ['a single line blockquote'],
        'blockquote2': [
            'a nested blockquote',
            {
                'with multiline': [
                    'the nested part'
                ]
            },
            'last line of the blockquote'
        ]
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict

def test_paragraphs():
    paragraphs = '''
A paragraph
a second paragraph

a paragraph after a empty row
'''
    md = Markdown(paragraphs)
    expected_list = [
        {'paragraph': 'A paragraph'},
        {'paragraph': 'a second paragraph'},
        {'paragraph': 'a paragraph after a empty row'}
    ]
    expected_dict = {
        'paragraph': 'A paragraph',
        'paragraph2': 'a second paragraph',
        'paragraph3': 'a paragraph after a empty row'
    }

    assert md.md_list == expected_list
    assert md.md_dict == expected_dict
