import rich

from markdown_to_data.markdown_to_data import Markdown


markdown_example: str = '''
---

title: Example
author: John Doe
tags: [python, code]

---
---

title: Example
author: John Doe
tags: [python, code]

---

Just text

# #Sample Markdown #Lists

## Lists

### Unordered Lists
- Item 1
- Item 2
    - Subitem 1
        - Subsubitem 1
    - Subitem 2
- Item 3

- Item 1
- Item 2

```Python

def hello_world():
    print('Hello World!)
```
```Python
def hello_world():
    print('Hello World!)
```

### Ordered List
4. First item reversed
3. Second item
    1. Subitem 1
    2. Subitem 2
2. Third item
---
1. First item
2. Second item

## Not a List

This is just regular text.

Again regular text

## Table
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |


| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

A definition list
: The definition of a list
: The next line of the definition
some text
A definition list
: The definition of a list
: The next line of the definition

some text
> Blockquote
>> Indent blockquote

> new blockquote
'''

markdown = Markdown(markdown_example)

rich.print(markdown.markdown_dict)
print(markdown.md_to_json())