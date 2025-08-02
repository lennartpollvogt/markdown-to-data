from src.markdown_to_data.to_python.merging_multiline_objects.merge_code import merge_code_blocks

def test_simple_code_block():
    classified_list = [
        {'code': '```python', 'indent': 0},
        {'code': 'print("Hello")', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    expected = [
        {'code': {'language': 'python', 'content': 'print("Hello")'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_code_block_with_surrounding_text():
    classified_list = [
        {'p': 'Before text'},
        {'code': '```', 'indent': 0},
        {'code': 'print("Hello")', 'indent': 0},
        {'code': '```', 'indent': 0},
        {'p': 'After text'}
    ]
    expected = [
        {'p': 'Before text'},
        {'code': {'language': None, 'content': 'print("Hello")'}, 'start_line': 0, 'end_line': 0},
        {'p': 'After text'}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_multiple_code_blocks():
    classified_list = [
        {'code': '```python', 'indent': 0},
        {'code': 'def hello():', 'indent': 0},
        {'code': '    print("Hello")', 'indent': 4},
        {'code': '```', 'indent': 0},
        {'p': 'Middle text'},
        {'code': '```javascript', 'indent': 0},
        {'code': 'console.log("Hello");', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    expected = [
        {'code': {'language': 'python', 'content': 'def hello():\n    print("Hello")'}, 'start_line': 0, 'end_line': 0},
        {'p': 'Middle text'},
        {'code': {'language': 'javascript', 'content': 'console.log("Hello");'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_empty_code_block():
    classified_list = [
        {'code': '```python', 'indent': 0},
        {'code': '', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    expected = [
        {'code': {'language': 'python', 'content': ''}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_indented_code_block():
    classified_list = [
        {'code': '```', 'indent': 4},
        {'code': '    print("Hello")', 'indent': 4},
        {'code': '    print("World")', 'indent': 4},
        {'code': '```', 'indent': 4}
    ]
    expected = [
        {'code': {'language': None, 'content': 'print("Hello")\nprint("World")'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_invalid_language_specification():
    classified_list = [
        {'code': '```invalid@language', 'indent': 0},
        {'code': 'print("Hello")', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    expected = [
        {'code': {'language': None, 'content': 'invalid@language\nprint("Hello")'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_code_block_with_special_characters():
    classified_list = [
        {'code': '```bash', 'indent': 0},
        {'code': '# Comment', 'indent': 0},
        {'code': 'echo "Hello * World"', 'indent': 0},
        {'code': '$PATH', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    expected = [
        {'code': {'language': 'bash', 'content': '# Comment\necho "Hello * World"\n$PATH'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected

def test_unclosed_code_block():
    classified_list = [
        {'code': '```python', 'indent': 0},
        {'code': 'print("Hello")', 'indent': 0}
    ]
    expected = [
        {'code': {'language': 'python', 'content': 'print("Hello")'}, 'start_line': 0, 'end_line': 0}
    ]
    assert merge_code_blocks(classified_list) == expected
