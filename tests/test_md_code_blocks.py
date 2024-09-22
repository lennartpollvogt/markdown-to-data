import pytest
from markdown_to_data.markdown_to_data import MarkdownMapper

@pytest.fixture
def md_converter():
    return MarkdownMapper()

def test_extract_code_block_without_language(md_converter):
    markdown = """
Some text before the code block

```
# Codeblock with leading text, but inside the code block

def example_func():
    return print("Hello world")
```

Some text after the code block
"""
    expected_result = {
        "language": None,
        "content": "# Codeblock with leading text, but inside the code block\ndef example_func():\n    return print(\"Hello world\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_extract_code_block_with_language(md_converter):
    markdown = """
Some text before the code block

```Python
def example_func():
    return print("Hello world")
```

Some text after the code block
"""
    expected_result = {
        "language": "python",
        "content": "def example_func():\n    return print(\"Hello world\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_no_code_block_found(md_converter):
    markdown = "This is just plain text without any code blocks."
    assert md_converter._extract_md_code(markdown) == {}

def test_multiple_code_blocks(md_converter):
    markdown = """
First code block:
```
print("Hello")
```

Second code block:
```python
print("World")
```
"""
    expected_result = {
        "language": None,
        "content": "print(\"Hello\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_code_block_at_start_of_text(md_converter):
    markdown = """```python
def hello_world():
    print("Hello, World!")
```
Text after the code block."""
    expected_result = {
        "language": "python",
        "content": "def hello_world():\n    print(\"Hello, World!\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_code_block_at_end_of_text(md_converter):
    markdown = """Text before the code block.
```python
def hello_world():
    print("Hello, World!")
```
"""
    expected_result = {
        "language": "python",
        "content": "def hello_world():\n    print(\"Hello, World!\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_empty_code_block(md_converter):
    markdown = """
```
```
"""
    expected_result = {
        "language": None,
        "content": ""
    }
    assert md_converter._extract_md_code(markdown) == expected_result

def test_code_block_within_paragraph(md_converter):
    markdown = "This is a paragraph with ```code``` inside it."
    assert md_converter._extract_md_code(markdown) == {}

# TODO: is this a real use case?
'''
def test_code_block_with_leading_whitespace(md_converter):
    markdown = """
   ```python
   def hello_world():
       print("Hello, World!")
   ```
   """
    expected_result = {
        "language": "python",
        "content": "def hello_world():\n    print(\"Hello, World!\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result
'''

# TODO: is this a real use case?
'''
def test_nested_code_blocks(md_converter):
    markdown = """
```python
def outer_function():
    print("Outer function")
    
    ```inner
    def inner_function():
        print("Inner function")
    ```
    
    print("Back in outer function")
```
"""
    expected_result = {
        "language": "python",
        "content": "def outer_function():\n    print(\"Outer function\")\n    \n    ```inner\n    def inner_function():\n        print(\"Inner function\")\n    ```\n    \n    print(\"Back in outer function\")"
    }
    assert md_converter._extract_md_code(markdown) == expected_result
'''
    

# pytest test_md_code_blocks.py