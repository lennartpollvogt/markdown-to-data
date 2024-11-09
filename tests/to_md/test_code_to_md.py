import pytest
from markdown_to_data.to_md.md_elements.to_md_code import code_data_to_md

def test_code_block_no_language():
    data = {
        'language': None,
        'content': "{'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],"
                  "'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}"
    }
    expected = (
        "```\n"
        "{'table': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}],"
        "'table2': [{'Column 1': 'Cell 1', 'Column 2': 'Cell 2'}]}\n"
        "```"
    )
    assert code_data_to_md(data) == expected

def test_code_block_with_language():
    data = {
        'language': 'python',
        'content': "def hello():\n    print('Hello World!')"
    }
    expected = (
        "```python\n"
        "def hello():\n"
        "    print('Hello World!')\n"
        "```"
    )
    assert code_data_to_md(data) == expected

def test_empty_code_block():
    data = {
        'language': 'python',
        'content': ''
    }
    expected = "```python\n\n```"
    assert code_data_to_md(data) == expected

def test_invalid_input():
    data = {}
    assert code_data_to_md(data) == ''

def test_missing_content():
    data = {'language': 'python'}
    assert code_data_to_md(data) == ''

def test_multiline_code():
    data = {
        'language': 'javascript',
        'content': "function test() {\n    const x = 1;\n    return x;\n}"
    }
    expected = (
        "```javascript\n"
        "function test() {\n"
        "    const x = 1;\n"
        "    return x;\n"
        "}\n"
        "```"
    )
    assert code_data_to_md(data) == expected

def test_code_with_special_characters():
    data = {
        'language': 'bash',
        'content': "echo 'Special * characters $ and # symbols'"
    }
    expected = (
        "```bash\n"
        "echo 'Special * characters $ and # symbols'\n"
        "```"
    )
    assert code_data_to_md(data) == expected

def test_non_string_content():
    data = {
        'language': 'python',
        'content': 42
    }
    expected = "```python\n42\n```"
    assert code_data_to_md(data) == expected

def test_none_content():
    data = {
        'language': 'python',
        'content': None
    }
    expected = "```python\nNone\n```"
    assert code_data_to_md(data) == expected
