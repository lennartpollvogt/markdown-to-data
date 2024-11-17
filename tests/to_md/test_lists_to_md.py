import pytest
from src.markdown_to_data.to_md.md_elements.to_md_lists import list_data_to_md

def test_ordered_list():
    data = {
        'type': 'ol',
        'list': [
            'Item 1',
            {'Item 2': ['Subitem 1', 'Subitem 2']},
            'Item 3'
        ]
    }
    expected = (
        "1. Item 1\n"
        "2. Item 2\n"
        "  1. Subitem 1\n"
        "  2. Subitem 2\n"
        "3. Item 3"
    )
    assert list_data_to_md(data) == expected

def test_unordered_list():
    data = {
        'type': 'ul',
        'list': [
            'Item 1',
            'Item 2',
            {'Item 3': ['Subitem 1', 'Subitem 2']}
        ]
    }
    expected = (
        "- Item 1\n"
        "- Item 2\n"
        "- Item 3\n"
        "  - Subitem 1\n"
        "  - Subitem 2"
    )
    assert list_data_to_md(data) == expected

def test_empty_list():
    data = {
        'type': 'ul',
        'list': []
    }
    assert list_data_to_md(data) == ''

def test_invalid_input():
    data = {}
    assert list_data_to_md(data) == ''

def test_deeply_nested_list():
    data = {
        'type': 'ul',
        'list': [
            {
                'Item 1': [
                    {
                        'Subitem 1': [
                            'Sub-subitem 1',
                            'Sub-subitem 2'
                        ]
                    }
                ]
            }
        ]
    }
    expected = (
        "- Item 1\n"
        "  - Subitem 1\n"
        "    - Sub-subitem 1\n"
        "    - Sub-subitem 2"
    )
    assert list_data_to_md(data) == expected

def test_mixed_nested_lists():
    data = {
        'type': 'ol',
        'list': [
            'Item 1',
            {
                'Item 2': [
                    'Subitem 1',
                    {
                        'Subitem 2': [
                            'Sub-subitem 1'
                        ]
                    }
                ]
            }
        ]
    }
    expected = (
        "1. Item 1\n"
        "2. Item 2\n"
        "  1. Subitem 1\n"
        "  2. Subitem 2\n"
        "    1. Sub-subitem 1"
    )
    assert list_data_to_md(data) == expected
