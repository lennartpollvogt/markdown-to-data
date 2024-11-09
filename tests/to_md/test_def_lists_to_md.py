import pytest
from markdown_to_data.to_md.md_elements.to_md_def_lists import definition_list_data_to_md

def test_simple_definition_list():
    data = {
        'term': 'First Term',
        'list': ['This is the definition of the first term.']
    }
    expected = (
        "First Term\n"
        ": This is the definition of the first term."
    )
    assert definition_list_data_to_md(data) == expected

def test_multiple_definitions():
    data = {
        'term': 'Second Term',
        'list': [
            'This is one definition of the second term.',
            'This is another definition of the second term.'
        ]
    }
    expected = (
        "Second Term\n"
        ": This is one definition of the second term.\n"
        ": This is another definition of the second term."
    )
    assert definition_list_data_to_md(data) == expected

def test_empty_definition_list():
    data = {
        'term': 'Empty Term',
        'list': []
    }
    expected = "Empty Term"
    assert definition_list_data_to_md(data) == expected

def test_invalid_input():
    data = {}
    assert definition_list_data_to_md(data) == ''

def test_missing_list():
    data = {'term': 'Term Only'}
    assert definition_list_data_to_md(data) == ''

def test_missing_term():
    data = {'list': ['Definition without term']}
    assert definition_list_data_to_md(data) == ''

def test_term_with_special_characters():
    data = {
        'term': 'Term: with: colons!',
        'list': ['Definition with special characters: !@#$%']
    }
    expected = (
        "Term: with: colons!\n"
        ": Definition with special characters: !@#$%"
    )
    assert definition_list_data_to_md(data) == expected

def test_multiline_definitions():
    data = {
        'term': 'Complex Term',
        'list': [
            'First line of definition.',
            'Second line of definition.',
            'Third line of definition.'
        ]
    }
    expected = (
        "Complex Term\n"
        ": First line of definition.\n"
        ": Second line of definition.\n"
        ": Third line of definition."
    )
    assert definition_list_data_to_md(data) == expected
