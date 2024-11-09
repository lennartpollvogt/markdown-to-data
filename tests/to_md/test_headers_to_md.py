import pytest
from markdown_to_data.to_md.md_elements.to_md_headers import header_data_to_md

def test_h1_header():
    data = {'h1': 'Testing the capabilities of `markdown-to-data`'}
    expected = "# Testing the capabilities of `markdown-to-data`"
    assert header_data_to_md(data) == expected

def test_h2_header():
    data = {'h2': 'Table section'}
    expected = "## Table section"
    assert header_data_to_md(data) == expected

def test_all_header_levels():
    test_content = "Header Test"
    for i in range(1, 7):
        data = {f'h{i}': test_content}
        expected = f"{'#' * i} {test_content}"
        assert header_data_to_md(data) == expected

def test_empty_input():
    data = {}
    assert header_data_to_md(data) == ''

def test_invalid_header_level():
    data = {'h7': 'Invalid header level'}
    assert header_data_to_md(data) == 'Invalid header level'

def test_none_input():
    assert header_data_to_md(None) == ''

def test_header_with_special_characters():
    data = {'h1': 'Header with *italic* and **bold**'}
    expected = "# Header with *italic* and **bold**"
    assert header_data_to_md(data) == expected

def test_header_with_code():
    data = {'h3': 'Header with `code`'}
    expected = "### Header with `code`"
    assert header_data_to_md(data) == expected

def test_header_with_numbers():
    data = {'h4': 'Header 123'}
    expected = "#### Header 123"
    assert header_data_to_md(data) == expected

def test_non_string_content():
    data = {'h1': 42}
    expected = "# 42"
    assert header_data_to_md(data) == expected
