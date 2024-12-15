# pytest tests/to_data/classification/test_classify_md_lists.py

import pytest
from src.markdown_to_data.to_python.classification.md_classification.classify_md_list import (
    is_unordered_list_item,
    is_ordered_list_item
)

@pytest.mark.parametrize(
    "line, expected",
    [
        # Valid unordered task list items - unchecked
        (
            "- [ ] unchecked item",
            (True, "unchecked item", "-", "unchecked", 6, 0)
        ),
        (
            "- [ ] ",
            (True, "", "-", "unchecked", 5, 0)
        ),
        (
            "  - [ ] indented unchecked",
            (True, "indented unchecked", "-", "unchecked", 8, 2)
        ),

        # Valid unordered task list items - checked
        (
            "- [x] checked item",
            (True, "checked item", "-", "checked", 6, 0)
        ),
        (
            "- [X] checked with capital X",
            (True, "checked with capital X", "-", "checked", 6, 0)
        ),

        # Normal unordered list items (not tasks)
        (
            "- regular item",
            (True, "regular item", "-", None, 2, 0)
        ),
        (
            "  - indented item",
            (True, "indented item", "-", None, 4, 2)
        ),

        # Invalid unordered list items
        (
            "-[ ] missing space",
            (False, "", "", None, 0, 0)
        ),
        (
            "- [] invalid brackets",
            (True, "[] invalid brackets", "-", None, 2, 0)
        ),
        (
            "",  # empty line
            (False, "", "", None, 0, 0)
        ),
    ]
)
def test_unordered_task_list(line: str, expected: tuple):
    """Test unordered list items including task lists."""
    stripped_line = line.strip()
    result = is_unordered_list_item(stripped_line, line)
    assert result == expected

@pytest.mark.parametrize(
    "line, expected",
    [
        # Valid ordered task list items - unchecked
        (
            "1. [ ] unchecked item",
            (True, "unchecked item", "1.", "unchecked", 7, 0)
        ),
        (
            "2. [ ] ",
            (True, "", "2.", "unchecked", 6, 0)
        ),
        (
            "  1. [ ] indented unchecked",
            (True, "indented unchecked", "1.", "unchecked", 9, 2)
        ),

        # Valid ordered task list items - checked
        (
            "1. [x] checked item",
            (True, "checked item", "1.", "checked", 7, 0)
        ),
        (
            "2. [X] checked with capital X",
            (True, "checked with capital X", "2.", "checked", 7, 0)
        ),

        # Normal ordered list items (not tasks)
        (
            "1. regular item",
            (True, "regular item", "1.", None, 3, 0)
        ),
        (
            "  2. indented item",
            (True, "indented item", "2.", None, 5, 2)
        ),

        # Invalid ordered list items
        (
            "1.[ ] missing space",
            (False, "", "", None, 0, 0)
        ),
        (
            "1. [] invalid brackets",
            (True, "[] invalid brackets", "1.", None, 3, 0)
        ),
    ]
)
def test_ordered_task_list(line: str, expected: tuple):
    """Test ordered list items including task lists."""
    stripped_line = line.strip()
    result = is_ordered_list_item(stripped_line, line)
    assert result == expected

def test_task_list_with_special_characters():
    """Test task list items containing special characters."""
    special_chars = "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"

    # Unordered task list
    ul_result = is_unordered_list_item(
        f"- [ ] {special_chars}",
        f"- [ ] {special_chars}"
    )
    assert ul_result == (True, special_chars, "-", "unchecked", 6, 0)

    # Ordered task list
    ol_result = is_ordered_list_item(
        f"1. [ ] {special_chars}",
        f"1. [ ] {special_chars}"
    )
    assert ol_result == (True, special_chars, "1.", "unchecked", 7, 0)

def test_task_list_unicode_content():
    """Test task list items with unicode characters."""
    unicode_content = "🐍 Python is 素晴らしい!"

    # Unordered task list
    ul_result = is_unordered_list_item(
        f"- [x] {unicode_content}",
        f"- [x] {unicode_content}"
    )
    assert ul_result == (True, unicode_content, "-", "checked", 6, 0)

    # Ordered task list
    ol_result = is_ordered_list_item(
        f"1. [x] {unicode_content}",
        f"1. [x] {unicode_content}"
    )
    assert ol_result == (True, unicode_content, "1.", "checked", 7, 0)

def test_task_list_extreme_indentation():
    """Test task list items with extreme indentation levels."""
    # Unordered list with spaces
    ul_space_task_result = is_unordered_list_item(
        "- [ ] deeply",
        "        - [ ] deeply"
    )
    assert ul_space_task_result == (True, "deeply", "-", "unchecked", 14, 8)

    # Ordered list with spaces
    ol_space_task_result = is_ordered_list_item(
        "1. [ ] deeply",
        "        1. [ ] deeply"
    )
    assert ol_space_task_result == (True, "deeply", "1.", "unchecked", 15, 8)

    # Unordered list with spaces
    ul_space_result = is_unordered_list_item(
        "-  deeply",
        "        -  deeply"
    )
    assert ul_space_result == (True, "deeply", "-", None, 11, 8)

    # Ordered list with spaces
    ol_space_result = is_ordered_list_item(
        "1.  deeply",
        "        1.  deeply"
    )
    assert ol_space_result == (True, "deeply", "1.", None, 12, 8)

def test_task_list_empty_lines():
    """Test task list behavior with empty or whitespace-only lines."""
    # Empty line
    assert is_unordered_list_item("", "") == (False, "", "", None, 0, 0)
    assert is_ordered_list_item("", "") == (False, "", "", None, 0, 0)

    # Whitespace only
    assert is_unordered_list_item("", "   ") == (False, "", "", None, 0, 0)
    assert is_ordered_list_item("", "   ") == (False, "", "", None, 0, 0)

    # Just checkbox
    ul_result = is_unordered_list_item("- [ ]   ", "   - [ ]   ")
    assert ul_result == (True, "", "-", "unchecked", 8, 3)

    ol_result = is_ordered_list_item("1. [ ]   ", "   1. [ ]   ")
    assert ol_result == (True, "", "1.", "unchecked", 9, 3)

    assert is_unordered_list_item("-[ ] item", "") == (False, "", "", None, 0, 0)
    assert is_ordered_list_item("1.[ ] item", "") == (False, "", "", None, 0, 0)
