# markdown-to-data
Convert markdown and its building blocks (tables, lists, code, etc.) into structured and easy processable data (Python list or dictionary)

[WIP]
This project is still work in progress and early state. The functionality is limited (see Status).

## Status
- [x] Detect, extract and convert markdown building blocks into Python data structures
- [x] Provide two formats for parsed markdown:
  - List format: Each building block as separate dictionary in a list
  - Dictionary format: Nested structure using headers as keys
- [x] Convert parsed markdown to JSON
- [x] Extract specific building blocks (e.g., only tables or lists)
- [ ] Provide comprehensive documentation
- [ ] Add Pydantic integration for data validation
- [x] Add more test coverage --> 50 test cases
- [ ] Publish on PyPI


**Table of content**:
- [Quick overview](#quick-overview)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Supported Markdown Elements](#supported-markdown-elements)
    - [Metadata](#metadata-yaml-frontmatter)
    - [Headers](#headers-h1-h6)
    - [Lists](#lists-ordered-and-unordered-with-nesting)
    - [Tables](#tables)
    - [Code blocks](#code-blocks-with-language-detection)
    - [Definition lists](#definition-lists)
    - [Blockquotes](#blockquotes)
    - [Paragraphs](#paragraphs)
- [Why?](#why-markdown-to-data)

## Quick Overview

### Installation
(!NOT WORKING! CURRENTLY NOT ON PyPI!)
```bash
pip install markdown-to-data
```

### Basic Usage
```python
from markdown_to_data import Markdown

markdown = """
---
title: Example text
author: John Doe
---

# Main Header

- Item 1
- Item 2
    - Subitem 1

## Table Example
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""

md = Markdown(markdown)

# Get parsed markdown as list
print(md.md_list)
# Each building block is a separate dictionary in the list

# Get parsed markdown as nested dictionary
print(md.md_dict)
# Headers are used as keys for nesting content

# Extract specific building blocks
print(md.get_md_building_blocks(blocks=['table']))
```

### Output Formats

#### List Format (`md.md_list`)
```python
[
    {'metadata': {'title': 'Example text', 'author': 'John Doe'}},
    {'h1': 'Main Header'},
    {'list': {'type': 'ul', 'list': [['Item 1'], ['Item 2', [['Subitem 1']]]]}},
    {'h2': 'Table Example'},
    {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}
]
```

#### Dictionary Format (`md.md_dict`)
```python
{
    'metadata': {'title': 'Example text', 'author': 'John Doe'},
    'Main Header': {
        'list': {'type': 'ul', 'list': [['Item 1'], ['Item 2', [['Subitem 1']]]]},
        'Table Example': {
            'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]
        }
    }
}
```

#### Building blocks (`md.get_md_building_blocks(blocks=['table'])`)
```python
[
    {
        'table': [
            {
                'Column 1': 'Cell 1',
                'Column 2': 'Cell 2'
            }
        ]
    }
]
```

## Supported Markdown Elements

### Metadata (YAML frontmatter)

```python
metadata = '''
---
title: Document
author: John Doe
date: 2023-12-20
---
'''

md_metadata = Markdown(metadata)
print(md_metadata.md_list)
print(md_metadata.md_dict)
```

**`md_list'**
```
[
    {
        'metadata': {
            'title': 'Document',
            'author': 'John Doe',
            'date': '2023-12-20'
        }
    }
]
```

**'md_dict`**
```
{'metadata': {'title': 'Document', 'author': 'John Doe', 'date': '2023-12-20'}}
```

### Headers (h1-h6)

```python
headers = '''
# Heading level 1

## Heading level 2

## Heading level 2

### Heading level 3

# Heading level 1 again
'''

md_headers = Markdown(headers)
print(md_headers.md_list)
print(md_headers.md_dict)
```

**`md_list'**
```
[
    {'h1': 'Heading level 1'},
    {'h2': 'Heading level 2'},
    {'h2': 'Heading level 2'},
    {'h3': 'Heading level 3'},
    {'h1': 'Heading level 1 again'}
]
```

**'md_dict`**
```
{
    'Heading level 1': {'Heading level 2': {'Heading level 3': {}}},
    'Heading level 1 again': {}
}
```

### Lists (ordered and unordered with nesting)

```python
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

md_lists = Markdown(lists)
print(md_lists.md_list)
print(md_lists.md_dict)
```

**`md_list'**
```
[
    {
        'list': {
            'type': 'ul',
            'list': [
                ['item 1'],
                ['item 2', [['subitem 1'], ['subitem 2']]],
                ['item 3']
            ]
        }
    },
    {'list': {'type': 'ol', 'list': [['item 1'], ['item 2'], ['item 3']]}}
]
```

**'md_dict`**
```
{
    'list': {
        'type': 'ul',
        'list': [
            ['item 1'],
            ['item 2', [['subitem 1'], ['subitem 2']]],
            ['item 3']
        ]
    },
    'list2': {'type': 'ol', 'list': [['item 1'], ['item 2'], ['item 3']]}
}
```

### Tables

```python
tables = '''
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
'''

md_tables = Markdown(tables)
print(md_tables.md_list)
print(md_tables.md_dict)
```

**`md_list'**
```
[
    {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]},
    {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}
]
```

**'md_dict`**
```
{
    'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],
    'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]
}
```

### Code blocks (with language detection)

```python
code = '''
´´´
{
    'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],
    'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]
}
´´´

´´´python
def hello():
    print('Hello World!')
´´´
'''

md_code = Markdown(code)
print(md_code.md_list)
print(md_code.md_dict)
```

**`md_list'**
```
[
    {
        'code': {
            'language': '{',
            'content': "    'table': [{'Column 1': 'Cell 1', 'Column 2':
'Cell 2'}],\n    'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]\n}"
        }
    },
    {
        'code': {
            'language': 'python',
            'content': "def hello():\n    print('Hello World!')"
        }
    }
]
```

**'md_dict`**
```
{
    'code': {
        'language': '{',
        'content': "    'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell
2'}],\n    'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]\n}"
    },
    'code2': {
        'language': 'python',
        'content': "def hello():\n    print('Hello World!')"
    }
}
```

### Definition lists

```python
def_lists = '''
term 1
: definition 1
: definition 2

term 2
: definition 1
: definition 2
'''

md_def_lists = Markdown(def_lists)
print(md_def_lists.md_list)
print(md_def_lists.md_dict)
```

**`md_list'**
```
[
    {
        'def_list': {
            'term': 'term 1',
            'list': ['definition 1', 'definition 2']
        }
    },
    {
        'def_list': {
            'term': 'term 2',
            'list': ['definition 1', 'definition 2']
        }
    }
]
```

**'md_dict`**
```
{
    'def_list': {
        'term': 'term 1',
        'list': ['definition 1', 'definition 2']
    },
    'def_list2': {
        'term': 'term 2',
        'list': ['definition 1', 'definition 2']
    }
}
```

### Blockquotes

```python
blockquotes = '''
> a single line blockquote

> a nested blockquote
> with multiline
>> the nested part
> last line of the blockquote
'''

md_blockquotes = Markdown(blockquotes)
print(md_blockquotes.md_list)
print(md_blockquotes.md_dict)
```

**`md_list'**
```
[
    {'blockquote': [['a single line blockquote']]},
    {
        'blockquote': [
            ['a nested blockquote'],
            ['with multiline'],
            [['the nested part']],
            ['last line of the blockquote']
        ]
    }
]
```

**'md_dict`**
```
{
    'blockquote': [['a single line blockquote']],
    'blockquote2': [
        ['a nested blockquote'],
        ['with multiline'],
        [['the nested part']],
        ['last line of the blockquote']
    ]
}
```

### Paragraphs

```python
paragraphs = '''
A paragraph
a second paragraph

a paragraph after a empty row
'''

md_paragraphs = Markdown(paragraphs)
rich.print(md_paragraphs.md_list)
rich.print(md_paragraphs.md_dict)
```

**`md_list'**
```
[
    {'paragraph': 'A paragraph'},
    {'paragraph': 'a second paragraph'},
    {'paragraph': 'a paragraph after a empty row'}
]
```

**'md_dict`**
```
{
    'paragraph': 'A paragraph',
    'paragraph2': 'a second paragraph',
    'paragraph3': 'a paragraph after a empty row'
}
```

## Why markdown-to-data?
This library focuses on converting markdown into structured data formats that are easy to process programmatically. It's particularly useful for:

- Working with LLMs that output markdown-formatted responses
- Extracting structured data from markdown documentation
- Processing markdown content in data pipelines
- Building automation tools that work with markdown content

## Limitations
- Some extended markdown flavors might not be supported
- Complex nested structures might need additional processing
- Currently only supports basic markdown elements

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
