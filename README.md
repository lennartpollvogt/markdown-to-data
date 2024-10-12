# markdown-to-data
Convert markdown and its buildings blocks (tables, lists, code, etc.) into structured and easy processable data (Python list or JSON array)

[WIP]
This project is still work in progress and early state. The functionality is limitted (see Status).

Status:
- [x] Detect, extract and convert markdown building blocks into a python dictionary
- [x] Store the python dictionary in a variable of the `Markdown` class
- [x] Function to respond the dictionary into a JSON
- [x] Clean up the code base. Add more strucutre.
- [x] Consider hierarchy of building blocks by headers (set `hierarchy` to `True`)
- [ ] Provide more documentation
- [ ] Experiment with Pydantic's BaseModel and the automatic creation of it with [datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/jsondata/)
- [ ] Additional function to extract different types of syntax like URLs or tags
- [x] Additional function to only get back a certain kind of building blocks (e.g. only tables or lists or both)
- [ ] Refactor and add more tests
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

## Quick overview

#### The `Markdown` class

`markdown-to-data` is able to convert markdown formatted text into processable data (`dict`) considering the hierarchy of each the building block.

Installation:
```
pip install markdown-to-data
```

Example:
```python
from markdown-to-data import Markdown

markdown = '''
---
title: Example text
author: John Doe
tags: [markdown, example]
---

# A h1 header

A paragraph below the h1 header
A new paragraph

## A h2 header with a list below

- Item 1
- Item 2
    - Subitem 1

# Another h1 header
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
'''

print(Markdown(markdown=markdown, hierarchy=False).markdown_list)
# >>> returns list of dictionaries. Each dicationary is a building block
print(Markdown(markdown=markdown, hierarchy=True).markdown_list)
# >>> returns a list of dictionaries providing a hierarchical structure based on headers
```

Output `hierarchy = False`:
```
[
    {
        'metadata': {
            'title': 'Example text',
            'author': 'John Doe',
            'tags': ['markdown', 'example']
        }
    },
    {'h1': 'A h1 header'},
    {'paragraph': 'A paragraph below the h1 header'},
    {'paragraph': 'A new paragraph'},
    {'h2': 'A h2 header with a list below'},
    {'list': {'type': 'ul', 'list': [['Item 1'], ['Item 2', [['Subitem 1']]]]}},
    {'h1': 'Another h1 header'},
    {
        'table': [
            {'Column 1': 'Cell 1', 'Column 2': 'Cell 2'},
            {'Column 1': 'Cell 3', 'Column 2': 'Cell 4'}
        ]
    }
]
```


Output `hierarchy = True`:
```
[
    {
        'metadata': {
            'title': 'Example text',
            'author': 'John Doe',
            'tags': ['markdown', 'example']
        }
    },
    {
        'h1': {
            'title': 'A h1 header',
            'content': [
                {'paragraph': 'A paragraph below the h1 header'},
                {'paragraph': 'A new paragraph'},
                {
                    'h2': {
                        'title': 'A h2 header with a list below',
                        'content': [
                            {
                                'list': {
                                    'type': 'ul',
                                    'list': [
                                        ['Item 1'],
                                        ['Item 2', [['Subitem 1']]]
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    },
    {
        'h1': {
            'title': 'Another h1 header',
            'content': [
                {
                    'table': [
                        {'Column 1': 'Cell 1', 'Column 2': 'Cell 2'},
                        {'Column 1': 'Cell 3', 'Column 2': 'Cell 4'}
                    ]
                }
            ]
        }
    }
]
```

#### Return specific building blocks

Take the example code above and add the following:

```python
# ... previous code

print(markdown2.get_md_building_blocks(blocks=['table', 'list']))
```

Output:
```
[
    {'list': {'type': 'ul', 'list': [['Item 1'], ['Item 2', [['Subitem 1']]]]}},
    {'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}, {'Column 1': 'Cell 3', 'Column 2': 'Cell 4'}]}
]
```

## Why?

Markdown is at least a structured format. The structured is built by the buildings blocks of the markdown syntax. Examples are headers starting with a `# ` and go up to six `###### `. Or lists starting with a `- `.
There are a lot of tools to convert markdown into HTML or wise verca. And you will as well find tool to convert markdown into JSON. But markdown comes with additional flavours which are not part of the common markdown syntax (e.g. tables, definition lists or fenced codeblocks) and in my research were not covered by the tools that I found.

I wanted the markdown to be converted into an easy to process format like a python dictionary or a JSON. It has to be reliable in a way that the output format for a certain building block has always the same structure to expect.

My intention with this library was to use it for my experiments with Large Language Models (LLMs). Due to the fact that they get trained text based, there is a lot of markdown formats being used in their training, why they are very good in responding in a markdown format. And now imagine letting the LLMs respond in markdown within a specific structure and you would be able to easily process the response. 

One example would be using a LLMs with vision capabilities to extract data from tables in images by letting the LLM respond in markdown and convert it from markdown into a python dictionary or JSON.

Another example would use the LLM to extract important information out of a text and sort them in lists or working with headers to get even the hierarchy and connections of the information out of the text.

Furthermore, extracting fenced code blocks can help building AI agents which are able to execute tasks by responding the code within the markdown format.

## Processable markdown building blocks

This library is able to process the following building blocks from markdown into a python dictionary and JSON.

### Metadata

Input:
```
---
title: Example text
author: John Doe
tags: [markdown, example]
---
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'metadata': {
        'title': 'Example text',
        'author': 'John Doe',
        'tags': ['markdown', 'example']
    }
}
```

### Headers

Input:
```markdown
# A h1 header
```

**General structure of a heading**:
Output (`hierarcy`= `True`):
```
{'h1': {'title': 'A h1 header', 'content': []}}
```
> In a hierarchical strucutred output `content` will contain all sub-items of `h1`

Output (`hierarcy`= `False`)
```
{'h1': 'A h1 header'}
```

### Lists

**Unordered lists**:

Input:
```
- Item 1
- Item 2
    - Subitem 1
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'list': {
        'type': 'ul', 
        'list': [
            [
                'Item 1'
            ], 
            [
                'Item 2', 
                [
                    [
                        'Subitem 1'
                    ]
                ]
            ]
        ]
    }
}
```

**Ordered lists**:

Input:
```
1. Item 1
2. Item 2
    1. Subitem 1
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'list': {
        'type': 'ol', 
        'list': [
            ['Item 1'], 
            [
                'Item 2', 
                [
                    [
                        'Subitem 1'
                    ]
                ]
            ]
        ]
    }
}
```

### Tables

Input:
```
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'table': [
        {
            'Column 1': 'Cell 1', 'Column 2': 'Cell 2'
        }, 
        {
            'Column 1': 'Cell 3', 'Column 2': 'Cell 4'
        }
    ]
}
```

### Code blocks

Input:
```python
def hello():
    print('Hello world!')
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'code': {
        'language': 'python', 
        'content': "def hello():\n    print('Hello world!')"
    }
}
```

### Definition lists

Input:
```
A term to define
: A definition for the term
: A second definition for the term
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'def_list': {
        'term': 'A term to define', 
        'list': [
            'A definition for the term', 
            'A second definition for the term'
        ]
    }
}
```

### Blockquotes

Input:
```
> Blockquote in frist level
>> Blockquote in second level
> Another blockquote in first level
```

Output (`hierarcy`= `True` OR `False`):
```
{
    'blockquote': [
        [
            'Blockquote in frist level'
        ], 
        [
            [
                'Blockquote in second level'
            ]
        ], 
        [
            'Another blockquote in first level'
        ]
    ]
}
```

**What are the limitations?**
- not all flavors of markdown are covered
