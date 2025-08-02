from src.markdown_to_data.to_python.classification.classification import classify_markdown_line_by_line


markdown = """
---
title: A test Markdown
tags: python, markdown, md, data
author: the owner
---

# Header 1
#No header just a paragraph to test header

> blockquote
 >this is also a blockquote
>> level 2

| column1 | column2 |
|---------|---------|
| cell 1  | cell 2  |
| cell 3  | cell 4
"""


def test_md_classification():
    result = classify_markdown_line_by_line(markdown=markdown)

    expected_result = [
        {'p': '', 'indent': 0, 'line': 1},
        {'hr': '---', 'indent': 0, 'line': 2},
        {'p': 'title: A test Markdown', 'indent': 0, 'line': 3},
        {'p': 'tags: python, markdown, md, data', 'indent': 0, 'line': 4},
        {'p': 'author: the owner', 'indent': 0, 'line': 5},
        {'hr': '---', 'indent': 0, 'line': 6},
        {'p': '', 'indent': 0, 'line': 7},
        {'h1': 'Header 1', 'indent': 0, 'line': 8},
        {'p': '#No header just a paragraph to test header', 'indent': 0, 'line': 9},
        {'p': '', 'indent': 0, 'line': 10},
        {'blockquote': 'blockquote', 'level': 1, 'line': 11},
        {'blockquote': 'this is also a blockquote', 'level': 1, 'line': 12},
        {'blockquote': 'level 2', 'level': 2, 'line': 13},
        {'p': '', 'indent': 0, 'line': 14},
        {'tr': {'td_1': 'column1', 'td_2': 'column2'}, 'indent': 0, 'line': 15},
        {'tr': 'table_separator', 'indent': 0, 'line': 16},
        {'tr': {'td_1': 'cell 1', 'td_2': 'cell 2'}, 'indent': 0, 'line': 17},
        {'tr': {'td_1': 'cell 3', 'td_2': 'cell 4'}, 'indent': 0, 'line': 18},
    ]

    assert result == expected_result
