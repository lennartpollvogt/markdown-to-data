# markdown-to-data
Convert markdown and its elements (tables, lists, code, etc.) into structured, easily processable data formats like lists and hierarchical dictionaries (or JSON), with support for parsing back to markdown.

## Status
- [x] Detect, extract and convert markdown building blocks into Python data structures
- [x] Provide two formats for parsed markdown:
  - [x] List format: Each building block as separate dictionary in a list
  - [x] Dictionary format: Nested structure using headers as keys
- [x] Convert parsed markdown to JSON
- [x] Parse markdown data back to markdown formatted string
  - [x] Add options which data gets parsed back to markdown
- [x] Extract specific building blocks (e.g., only tables or lists)
- [x] Support for task lists (checkboxes)
- [x] Enhanced code block handling with language detection
- [x] Comprehensive blockquote support with nesting
- [x] Consistent handling of definition lists
- [x] Provide comprehensive documentation
- [x] Add more test coverage --> 215 test cases
- [x] Publish on PyPI
- [ ] Align with edge cases of [Common Markdown Specification](https://spec.commonmark.org/0.31.2/)

## Quick Overview

### Install
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

- [ ] Pending task
    - [x] Completed subtask
- [x] Completed task

## Table Example
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

´´´python
def hello():
    print("Hello World!")
´´´
"""

md = Markdown(markdown)

# Get parsed markdown as list
print(md.md_list)
# Each building block is a separate dictionary in the list

# Get parsed markdown as nested dictionary
print(md.md_dict)
# Headers are used as keys for nesting content

# Get information about markdown elements
print(md.md_elements)
```

### Output Formats

#### List Format (`md.md_list`)
```python
[
    {'metadata': {'title': 'Example text', 'author': 'John Doe'}},
    {'header': {'level': 1, 'content': 'Main Header'}},
    {
        'list': {
            'type': 'ul',
            'items': [
                {
                    'content': 'Pending task',
                    'items': [
                        {
                            'content': 'Completed subtask',
                            'items': [],
                            'task': 'checked'
                        }
                    ],
                    'task': 'unchecked'
                },
                {'content': 'Completed task', 'items': [], 'task': 'checked'}
            ]
        }
    },
    {'header': {'level': 2, 'content': 'Table Example'}},
    {'table': {'Column 1': ['Cell 1'], 'Column 2': ['Cell 2']}},
    {
        'code': {
            'language': 'python',
            'content': 'def hello():\n    print("Hello World!")'
        }
    }
]
```

#### Dictionary Format (`md.md_dict`)
```python
{
    'metadata': {'title': 'Example text', 'author': 'John Doe'},
    'Main Header': {
        'list_1': {
            'type': 'ul',
            'items': [
                {
                    'content': 'Pending task',
                    'items': [
                        {
                            'content': 'Completed subtask',
                            'items': [],
                            'task': 'checked'
                        }
                    ],
                    'task': 'unchecked'
                },
                {'content': 'Completed task', 'items': [], 'task': 'checked'}
            ]
        },
        'Table Example': {
            'table_1': {'Column 1': ['Cell 1'], 'Column 2': ['Cell 2']},
            'code_1': {
                'language': 'python',
                'content': 'def hello():\n    print("Hello World!")'
            }
        }
    }
}
```

#### MD Elements (`md.md_elements`)
```python
{
    'metadata': {'count': 1, 'positions': [0], 'variants': set()},
    'header': {'count': 2, 'positions': [1, 3], 'variants': set()},
    'list': {'count': 1, 'positions': [2], 'variants': {'ul'}},
    'table': {'count': 1, 'positions': [4], 'variants': set()},
    'code': {'count': 1, 'positions': [5], 'variants': {'python'}}
}
```

### Parse back to markdown (`to_md`)

The `Markdown` class provides a method to parse markdown data back to markdown-formatted strings.
The `to_md` method comes with options to customize the output:

```python
from markdown_to_data import Markdown

markdown = """
---
title: Example
---

# Main Header

- [x] Task 1
    - [ ] Subtask
- [ ] Task 2

## Code Example
´´´python
print("Hello")
´´´
"""

md = Markdown(markdown)
```

**Example 1**: Include specific elements
```python
print(md.to_md(
    include=['header', 'list'],  # Include all headers and lists
    spacer=1  # One empty line between elements
))
```

Output:
```markdown
# Main Header

- [x] Task 1
    - [ ] Subtask
- [ ] Task 2
```

**Example 2**: Include by position and exclude specific types
```python
print(md.to_md(
    include=[0, 1, 2],  # Include first three elements
    exclude=['code'],   # But exclude any code blocks
    spacer=2           # Two empty lines between elements
))
```

Output:
```markdown
---
title: Example
---


# Main Header


- [x] Task 1
    - [ ] Subtask
- [ ] Task 2
```

#### Using `to_md_parser` Function

The `to_md_parser` function can be used directly to convert markdown data structures to markdown text:

```python
from markdown_to_data import to_md_parser

data = [
    {
        'metadata': {
            'title': 'Document'
        }
    },
    {
        'header': {
            'level': 1,
            'content': 'Title'
        }
    },
    {
        'list': {
            'type': 'ul',
            'items': [
                {
                    'content': 'Task 1',
                    'items': [],
                    'task': 'checked'
                }
            ]
        }
    }
]

print(to_md_parser(data=data, spacer=1))
```

Output:
```markdown
---
title: Document
---

# Title

- [x] Task 1
```

## Supported Markdown Elements

### Metadata (YAML frontmatter)

```python
metadata = '''
---
title: Document
author: John Doe
tags: markdown, documentation
---
'''

md = Markdown(metadata)
print(md.md_list)
```

Output:
```python
[
    {
        'metadata': {
            'title': 'Document',
            'author': 'John Doe',
            'tags': ['markdown', 'documentation']
        }
    }
]
```

### Headers

```python
headers = '''
# Main Title
## Section
### Subsection
'''

md = Markdown(headers)
print(md.md_list)
```

Output:
```python
[
    {
        'header': {
            'level': 1,
            'content': 'Main Title'
        }
    },
    {
        'header': {
            'level': 2,
            'content': 'Section'
        }
    },
    {
        'header': {
            'level': 3,
            'content': 'Subsection'
        }
    }
]
```

### Lists (Including Task Lists)

```python
lists = '''
- Regular item
    - Nested item
- [x] Completed task
    - [ ] Pending subtask
1. Ordered item
    1. Nested ordered
'''

md = Markdown(lists)
print(md.md_list)
```

Output:
```python
[
    {
        'list': {
            'type': 'ul',
            'items': [
                {
                    'content': 'Regular item',
                    'items': [
                        {'content': 'Nested item', 'items': [], 'task': None}
                    ],
                    'task': None
                },
                {
                    'content': 'Completed task',
                    'items': [
                        {
                            'content': 'Pending subtask',
                            'items': [],
                            'task': 'unchecked'
                        }
                    ],
                    'task': 'checked'
                }
            ]
        }
    },
    {
        'list': {
            'type': 'ol',
            'items': [
                {
                    'content': 'Ordered item',
                    'items': [
                        {'content': 'Nested ordered', 'items': [], 'task': None}
                    ],
                    'task': None
                }
            ]
        }
    }
]
```

### Tables

```python
tables = '''
| Header 1 | Header 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |
'''

md = Markdown(tables)
print(md.md_list)
```

Output:
```python
[
    {
        'table': {
            'Header 1': ['Value 1', 'Value 3'],
            'Header 2': ['Value 2', 'Value 4']
        }
    }
]
```

### Code Blocks

```python
code = '''
´´´python
def example():
    return "Hello"
´´´

´´´javascript
console.log("Hello");
´´´
'''

md = Markdown(code)
print(md.md_list)
```

Output:
```python
[
    {
        'code': {
            'language': 'python',
            'content': 'def example():\n    return "Hello"'
        }
    },
    {
        'code': {
            'language': 'javascript',
            'content': 'console.log("Hello");'
        }
    }
]
```

### Blockquotes

```python
blockquotes = '''
> Simple quote
> Multiple lines

> Nested quote
>> Inner quote
> Back to outer
'''

md = Markdown(blockquotes)
print(md.md_list)
```

Output:
```python
[
    {
        'blockquote': [
            {'content': 'Simple quote', 'items': []},
            {'content': 'Multiple lines', 'items': []}
        ]
    },
    {
        'blockquote': [
            {
                'content': 'Nested quote',
                'items': [
                    {'content': 'Inner quote', 'items': []}
                ]
            },
            {'content': 'Back to outer', 'items': []}
        ]
    }
]
```

### Definition Lists

```python
def_lists = '''
Term
: Definition 1
: Definition 2
'''

md = Markdown(def_lists)
print(md.md_list)
```

Output:
```python
[
    {
        'def_list': {
            'term': 'Term',
            'list': ['Definition 1', 'Definition 2']
        }
    }
]
```

## Limitations
- Some extended markdown flavors might not be supported
- Inline formatting (bold, italic, links) is currently not parsed
- Table alignment specifications are not preserved

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an issue.
