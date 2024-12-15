from src.markdown_to_data.to_python.classification.classification import md_classification

def test_simple_code_block():
    markdown = '''```
print("Hello")
```'''
    expected = [
        {'code': '```', 'indent': 0},
        {'code': 'print("Hello")', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_code_block_with_language():
    markdown = '''```python
def hello():
    print("World")
```'''
    expected = [
        {'code': '```python', 'indent': 0},
        {'code': 'def hello():', 'indent': 0},
        {'code': '    print("World")', 'indent': 4},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_indented_code_block():
    markdown = '''    ```
    code here
    ```'''
    expected = [
        {'code': '```', 'indent': 0}, # TODO: this might be a problem
        {'code': '    code here', 'indent': 4},
        {'code': '    ```', 'indent': 4}
    ]
    assert md_classification(markdown) == expected

def test_code_block_with_surrounding_text():
    markdown = '''Some text
```
code
```
More text'''
    expected = [
        {'p': 'Some text', 'indent': 0},
        {'code': '```', 'indent': 0},
        {'code': 'code', 'indent': 0},
        {'code': '```', 'indent': 0},
        {'p': 'More text', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_empty_code_block():
    markdown = '''```
```'''
    expected = [
        {'code': '```', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_nested_code_block_markers():
    markdown = '''```
echo "```"
```'''
    expected = [
        {'code': '```', 'indent': 0},
        {'code': 'echo "```"', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_code_block_with_special_characters():
    markdown = '''```bash
echo "Hello * World"
# Comment
$PATH
```'''
    expected = [
        {'code': '```bash', 'indent': 0},
        {'code': 'echo "Hello * World"', 'indent': 0},
        {'code': '# Comment', 'indent': 0},
        {'code': '$PATH', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected

def test_multiple_code_blocks():
    markdown = '''```python
def a():
    pass
```
Some text
```javascript
console.log("Hi");
```'''
    expected = [
        {'code': '```python', 'indent': 0},
        {'code': 'def a():', 'indent': 0},
        {'code': '    pass', 'indent': 4},
        {'code': '```', 'indent': 0},
        {'p': 'Some text', 'indent': 0},
        {'code': '```javascript', 'indent': 0},
        {'code': 'console.log("Hi");', 'indent': 0},
        {'code': '```', 'indent': 0}
    ]
    assert md_classification(markdown) == expected
