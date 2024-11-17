import pytest
from src.markdown_to_data.to_md.md_elements.to_md_paragraphs import paragraph_data_to_md

def test_simple_paragraph():
    data = {'paragraph': 'some paragraph'}
    expected = "some paragraph"
    assert paragraph_data_to_md(data) == expected

def test_direct_string_input():
    data = "some paragraph"
    expected = "some paragraph"
    assert paragraph_data_to_md(data) == expected

def test_empty_paragraph():
    data = {'paragraph': ''}
    expected = ""
    assert paragraph_data_to_md(data) == expected

def test_none_value():
    data = {'paragraph': None}
    expected = "None"
    assert paragraph_data_to_md(data) == expected

def test_invalid_input():
    data = {}
    expected = ""
    assert paragraph_data_to_md(data) == expected

def test_paragraph_with_special_characters():
    data = {'paragraph': 'Special *characters* and **markdown** syntax!'}
    expected = "Special *characters* and **markdown** syntax!"
    assert paragraph_data_to_md(data) == expected

def test_paragraph_with_numbers():
    data = {'paragraph': 'Paragraph with number 42'}
    expected = "Paragraph with number 42"
    assert paragraph_data_to_md(data) == expected

def test_multiline_paragraph():
    data = {'paragraph': 'First line\nSecond line'}
    expected = "First line\nSecond line"
    assert paragraph_data_to_md(data) == expected

def test_paragraph_with_urls():
    data = {'paragraph': 'Check out https://example.com'}
    expected = "Check out https://example.com"
    assert paragraph_data_to_md(data) == expected
