import pytest
from src.markdown_to_data.to_data.joining_and_extraction.extraction import MarkdownExtractor
from src.markdown_to_data.markdown_to_data import Markdown

@pytest.fixture
def mapper():
    """Fixture to initialize the MarkdownMapper instance."""
    return MarkdownExtractor()

def test_extract_md_list_unordered(mapper):
    markdown_with_list = """
- Item 1
- Item 2
- Item 3
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ul",
        "list": ["Item 1", "Item 2", "Item 3"]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_unordered_from_two(mapper):
    markdown_with_list = """
- Item 1
- Item 2
- Item 3

- Audi
- Volkswagen
- Honda
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ul",
        "list": ["Item 1", "Item 2", "Item 3"]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_ordered(mapper):
    markdown_with_list = """
1. First item
2. Second item
3. Third item
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ol",
        "list": ["First item", "Second item", "Third item"]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_nested_unordered(mapper):
    markdown_with_list = """
- Item 1
- Item 2
  - Nested Item 1
  - Nested Item 2
- Item 3
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ul",
        "list": [
            "Item 1",
            {"Item 2": ["Nested Item 1", "Nested Item 2"]},
            "Item 3"
        ]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_nested_ordered(mapper):
    markdown_with_list = """
1. First item
2. Second item
   1. Nested first
   2. Nested second
3. Third item
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ol",
        "list": [
            "First item",
            {"Second item": ["Nested first", "Nested second"]},
            "Third item"
        ]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_mixed_unordered(mapper):
    markdown_with_list = """
- First unordered item
- Second unordered item
  1. Nested ordered 1
  2. Nested ordered 2
- Third unordered item
    """

    result = mapper._extract_md_list(markdown_with_list)
    expected = {
        "type": "ul",
        "list": [
            "First unordered item",
            {"Second unordered item": ["Nested ordered 1", "Nested ordered 2"]},
            "Third unordered item"
        ]
    }

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_empty(mapper):
    markdown_with_empty_list = """
    """

    result = mapper._extract_md_list(markdown_with_empty_list)
    expected = {}

    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_list_non_list_content(mapper):
    markdown_without_list = """
This is a paragraph.
It contains some text, but no lists.
    """

    result = mapper._extract_md_list(markdown_without_list)
    expected = {}

    assert result == expected, f"Expected {expected}, but got {result}"

def test_markdown_class_with_list():
    input_text = '''
- item 1
- item 2
    - subitem 1
    - subitem 2
- item 3
'''

    expected_output_list = [
        {
            'list': {
                'type': 'ul',
                'list': [
                    "item 1",
                    {"item 2": ["subitem 1", "subitem 2"]},
                    "item 3"
                ]
            }
        }
    ]
    expected_output_dict = {
        'list': {
            'type': 'ul',
            'list': [
                "item 1",
                {"item 2": ["subitem 1", "subitem 2"]},
                "item 3"
            ]
        }
    }

    markdown = Markdown(input_text)
    assert markdown.md_list == expected_output_list
    assert markdown.md_dict == expected_output_dict

def test_markdown_class_with_multiple_lists():
    input_text = '''
- item 1
- item 2
    - subitem 1
    - subitem 2
- item 3

- item 1

1. item 1
2. item 2
'''

    expected_output_list = [
        {
            'list': {
                'type': 'ul',
                'list': [
                    "item 1",
                    {"item 2": ["subitem 1", "subitem 2"]},
                    "item 3"
                ]
            }
        },
        {
            'list': {
                'type': 'ul',
                'list': ["item 1"]
            }
        },
        {
            'list': {
                'type': 'ol',
                'list': ["item 1", "item 2"]
            }
        }
    ]
    expected_output_dict = {
        'list': {
            'type': 'ul',
            'list': [
                "item 1",
                {"item 2": ["subitem 1", "subitem 2"]},
                "item 3"
            ]
        },
        'list2': {
            'type': 'ul',
            'list': ["item 1"]
        },
        'list3': {
            'type': 'ol',
            'list': ["item 1", "item 2"]
        }
    }

    markdown = Markdown(input_text)
    assert markdown.md_list == expected_output_list
    assert markdown.md_dict == expected_output_dict
