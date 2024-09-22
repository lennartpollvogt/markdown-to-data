import pytest
from markdown_to_data.markdown_to_data import MarkdownMapper

@pytest.fixture
def mapper():
    """Fixture to initialize the MarkdownMapper instance."""
    return MarkdownMapper()

def test_extract_md_def_list_single(mapper):
    markdown_with_def_list = """
Term 1
: Definition for term 1
"""
    result = mapper._extract_md_def_list(markdown_with_def_list)
    expected = {
        "term": "Term 1",
        "list": ["Definition for term 1"]
    }
    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_def_list_from_two(mapper):
    markdown_with_def_list = """
Term 1
: Definition for term 1
: Another definition for term 1

Term 2
: Definition for term 2
"""
    result = mapper._extract_md_def_list(markdown_with_def_list)
    expected = {
            "term": "Term 1",
            "list": ["Definition for term 1", "Another definition for term 1"]
        }
    assert result == expected, f"Expected {expected}, but got {result}"

# pytest test_def_lists.py