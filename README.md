# markdown-to-data
Convert markdown and its elements (tables, lists, code, etc.) into structured, easily processable data formats like lists and hierarchical dictionaries (or JSON), with support for parsing back to markdown.

[WIP]
This project is still work in progress and early state. The functionality is limited (see Status).

## Status
- [x] Detect, extract and convert markdown building blocks into Python data structures
- [x] Provide two formats for parsed markdown:
  - [x] List format: Each building block as separate dictionary in a list
  - [x] Dictionary format: Nested structure using headers as keys
- [x] Convert parsed markdown to JSON
- [x] Parse markdown data back to markdown formatted string
  - [x] add options which data gets parsed back to markdown
- [x] Extract specific building blocks (e.g., only tables or lists)
- [ ] Provide comprehensive documentation
- [ ] Add Pydantic integration for data validation
- [x] Add more test coverage --> 50 test cases
- [ ] Publish on PyPI


**Table of content**:
- [Quick overview](#quick-overview)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Parse back to markdown](#parse-back-to-markdown-to_md)
- [Supported Markdown Elements](#supported-markdown-elements)
    - [Metadata](#metadata-yaml-frontmatter)
    - [Headers](#headers-h1-h6)
    - [Lists](#lists-ordered-and-unordered-with-nesting)
    - [Tables](#tables)
    - [Code blocks](#code-blocks-with-language-detection)
    - [Definition lists](#definition-lists)
    - [Blockquotes](#blockquotes)
    - [Paragraphs](#paragraphs)
    - [Separator](#separator)
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

# Get a list of markdown elements included in the markdown file, the number of their appearance, the position and types
print(md.md_elements)

# Get the nested dictionary as a JSON string
print(md.to_json(indent=4))

# Extract specific building blocks
print(md.get_md_building_blocks(blocks=['table']))
```

### Output Formats

#### List Format (`md.md_list`)
```python
[
    {'metadata': {'title': 'Example text', 'author': 'John Doe'}},
    {'h1': 'Main Header'},
    {
        'list': {
            'type': 'ul',
            'list': ['Item 1', {'Item 2': ['Subitem 1']}]
        }
    },
    {'h2': 'Table Example'},
    {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}
]
```

#### Dictionary Format (`md.md_dict`)
```python
{
    'metadata': {'title': 'Example text', 'author': 'John Doe'},
    'Main Header': {
        'list': {
            'type': 'ul',
            'list': ['Item 1', {'Item 2': ['Subitem 1']}]
        },
        'Table Example': {
            'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]
        }
    }
}
```

#### MD Elements (`md.md_elements`)

Get information about all markdown elements in the markdown file.
The output is based on `md_list` and can be used for navigate through `md_list`

```python
{
    'metadata': {'count': 1, 'positions': [0], 'variants': set()},
    'h1': {'count': 1, 'positions': [1], 'variants': set()},
    'list': {'count': 1, 'positions': [2], 'variants': {'ul'}},
    'h2': {'count': 1, 'positions': [3], 'variants': set()},
    'table': {'count': 1, 'positions': [4], 'variants': set()}
}
```


#### JSON (`md.to_json(indent=4)`)

Converts the `md_dict` to a JSON string. By applying `ìndent` you can specify the indents for the output.

```
{
    'metadata': {'title': 'Example text', 'author': 'John Doe'},
    'Main Header': {
        'list': {
            'type': 'ul',
            'list': ['Item 1', {'Item 2': ['Subitem 1']}]
        },
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

### Parse back to markdown (`to_md`)

The `Markdown` class comes as well with a method to parse the data of markdown elements back to markdown formatted strings.
The method is called `to_md` and comes with some arguments to manipulate the outcome.

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
```

**Example 1**: include all and exclude nothing
```python
print(md.to_md(
    include=['headers', 'list', 4], # A list of markdown elements that will by included (here: all headers, the list and the fifth elements)
    exclude=[1], # the default value is None; markdown elements will be excluded based on the index in this argument;
    spacer=1 # the default value; defines how many empty lines will be added after each markdown element
))
```

Output:
```
# Main Header

- Item 1
- Item 2
  - Subitem 1

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Example 2**: `exclude` overwrites `include` and two `spacer`s
```python
print(md.to_md(
    include=['all'], # the default value; will include all markdown elements
    exclude=['h2', 3], # will overwrite `include` and exclude h2 headers and the fourth element (here: the list)
    spacer=2 # adds two empty line after each markdown elements which gets parsed
))
```

Output:
```
---
title: Example text
author: John Doe
---


# Main Header


| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Example 3**: `exclude` = `['all']` excludes everything and returns an empty line
```python
print(md.to_md(
    include=['h1', 'list', 'table'],
    exclude=['all'], # will overwrite the `include``and exclude all markdown elements
    spacer=1
))
```

Output:
```

```

#### `to_md_parser` function

**Note**: you can use the function `to_md_parser` to parse a list of dictionaries of markdown elements to markdown.

```python
from markdown_to_data import to_md_parser

example = [
    {
        'metadata': {
            'title': 'Test Document',
            'date': '2024-01-01'
        }
    },
    {'h1': 'Main Title'},
    {'paragraph': 'Sample paragraph'},
    {'h2': 'Subtitle'},
    {'list': {
        'type': 'ul',
        'list': ['Item 1', 'Item 2']
    }}
]

markdown_string = to_md_parser(data=example, spacer=1)

print(markdown_string)
```

Output:
```
---
title: Test Document
date: 2024-01-01
---

# Main Title

Sample paragraph

## Subtitle

- Item 1
- Item 2
```

## Supported Markdown Elements

### Metadata (YAML frontmatter)

A metadata block can only appear once in the markdown file and must be at the beginning.

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
                'item 1',
                {'item 2': ['subitem 1', 'subitem 2']},
                'item 3'
            ]
        }
    },
    {'list': {'type': 'ol', 'list': ['item 1', 'item 2', 'item 3']}}
]
```

**'md_dict`**
```
{
    'list': {
        'type': 'ul',
        'list': [
            'item 1',
            {'item 2': ['subitem 1', 'subitem 2']},
            'item 3'
        ]
    },
    'list2': {'type': 'ol', 'list': ['item 1', 'item 2', 'item 3']}
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
    {'blockquote': ['a single line blockquote']},
    {
        'blockquote': [
            'a nested blockquote',
            {'with multiline': ['the nested part']},
            'last line of the blockquote'
        ]
    }
]
```

**'md_dict`**
```
{
    'blockquote': ['a single line blockquote'],
    'blockquote2': [
        'a nested blockquote',
        {'with multiline': ['the nested part']},
        'last line of the blockquote'
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

### Separator

As described in the example for [Metadata](#metadata) a metadata block must appear at the very beginning of a markdown file. Later in the file a combination of three `-` (=`---`) will be classified as a separator.

```python
separator = '''
---
'''

md_separator = Markdown(separator)
print(md_separator.md_list)
print(md_separator.md_dict)
```

**`md_list'**
```
[
    {'separator': '---'}
]
```

**'md_dict`**
```
{
    'separator': '---'
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
