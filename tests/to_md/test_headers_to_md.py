from src.markdown_to_data.to_md.md_elements.to_md_headers import header_data_to_md

def test_basic_h1():
    data = {'header': {'level': 1, 'content': 'Basic Title'}}
    expected = "# Basic Title"
    assert header_data_to_md(data) == expected

def test_basic_h2():
    data = {'header': {'level': 2, 'content': 'Subtitle'}}
    expected = "## Subtitle"
    assert header_data_to_md(data) == expected

def test_all_header_levels():
    for level in range(1, 7):
        data = {'header': {'level': level, 'content': f'Header {level}'}}
        expected = f"{'#' * level} Header {level}"
        assert header_data_to_md(data) == expected

def test_with_empty_content():
    data = {'header': {'level': 1, 'content': ''}}
    expected = "# "
    assert header_data_to_md(data) == expected

def test_with_whitespace_content():
    data = {'header': {'level': 1, 'content': '   Spaced Content   '}}
    expected = "# Spaced Content"
    assert header_data_to_md(data) == expected

def test_with_invalid_level():
    data = {'header': {'level': 7, 'content': 'Invalid'}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_zero_level():
    data = {'header': {'level': 0, 'content': 'Invalid'}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_negative_level():
    data = {'header': {'level': -1, 'content': 'Invalid'}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_non_integer_level():
    data = {'header': {'level': '1', 'content': 'Invalid'}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_missing_content():
    data = {'header': {'level': 1}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_missing_level():
    data = {'header': {'content': 'Missing Level'}}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_empty_input():
    data = {}
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_none_input():
    data = None
    expected = ""
    assert header_data_to_md(data) == expected

def test_with_non_string_content():
    data = {'header': {'level': 1, 'content': 123}}
    expected = "# 123"
    assert header_data_to_md(data) == expected
