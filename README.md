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
- [ ] Add more test coverage
- [ ] Publish on PyPI


**Table of content**:
- [Quick overview](#quick-overview)
- [Why?](#why)
- [Processable markdown building blocks](#processable-markdown-building-blocks)
    - [Metadata](#metadata)
    - [Headers](#headers)
    - [Lists](#lists)
    - [Tables](#tables)
    - [Code blocks](#code-blocks)
    - [Definition lists](#definition-lists)
    - [Blockquotes](#blockquotes)

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
- Metadata (YAML frontmatter)
- Headers (h1-h6)
- Lists (ordered and unordered with nesting)
- Tables
- Code blocks (with language detection)
- Definition lists
- Blockquotes
- Paragraphs

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
