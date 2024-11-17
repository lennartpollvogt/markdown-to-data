import pytest
from src.markdown_to_data.to_md.md_elements.to_md_blockquotes import blockquote_data_to_md

def test_simple_blockquote():
    data = {'blockquote': ['A simple blockquote']}
    expected = "> A simple blockquote"
    assert blockquote_data_to_md(data) == expected

def test_multiline_blockquote():
    data = {
        'blockquote': [
            'First line',
            'Second line',
            'Third line'
        ]
    }
    expected = "> First line\n> Second line\n> Third line"
    assert blockquote_data_to_md(data) == expected

def test_nested_blockquote():
    data = {
        'blockquote': [
            {
                'Level one': [
                    {
                        'Level two': [
                            'Level three'
                        ]
                    }
                ]
            }
        ]
    }
    expected = "> Level one\n>> Level two\n>>> Level three"
    assert blockquote_data_to_md(data) == expected

def test_mixed_nesting_levels():
    data = {
        'blockquote': [
            {
                'First level': [
                    'Second level'
                ]
            },
            {
                'Back to first': [
                    'Deep level'
                ]
            }
        ]
    }
    expected = "> First level\n>> Second level\n> Back to first\n>> Deep level"
    assert blockquote_data_to_md(data) == expected

def test_empty_blockquote():
    data = {'blockquote': []}
    expected = ""
    assert blockquote_data_to_md(data) == expected

def test_invalid_input():
    data = {}
    expected = ""
    assert blockquote_data_to_md(data) == expected

def test_deeply_nested_blockquote():
    data = {
        'blockquote': [
            'Five levels deep'
        ]
    }
    expected = "> Five levels deep"
    assert blockquote_data_to_md(data) == expected


def test_mixed_content_types():
    data = {
        'blockquote': [
            'String',
            123,  # number
            True  # boolean
        ]
    }
    expected = "> String\n> 123\n> True"
    assert blockquote_data_to_md(data) == expected
